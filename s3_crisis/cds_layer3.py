# s3_crisis/cds_layer3.py
# Layer 3 — History Trend Analysis
# Mendeteksi pola berbahaya dari riwayat distress_score antar pesan.
# Tidak butuh model ML — murni analisis statistik, < 5ms.
#
# Layer 3 menjawab pertanyaan yang tidak bisa dijawab L1 atau L2:
# "Apakah kondisi user memburuk secara konsisten dari waktu ke waktu?"

from dataclasses import dataclass

# ── Threshold ─────────────────────────────────────────────────────────────
SPIKE_DELTA        = 0.25   # Kenaikan distress dalam 1 pesan → spike (lebih sensitif: 0.30→0.25)
HIGH_DISTRESS_THR  = 0.65   # Ambang batas "distress tinggi"
HIGH_DISTRESS_MIN  = 3      # Berapa pesan berturut-turut di atas threshold (lebih sensitif: 4→3)
TREND_MIN_POINTS   = 3      # Minimal berapa pesan untuk hitung tren
EXHAUSTION_DROP    = 0.12   # Penurunan sementara sebelum naik lagi (lebih sensitif: 0.15→0.12)
RAPID_DECLINE_DELTA = 0.40  # Terjadi penurunan DRASTIS lalu spike (warning sign)

# ── Output ────────────────────────────────────────────────────────────────
@dataclass
class Layer3Result:
    score      : float       # skor kontribusi ke CDS (0.0 – 0.40)
    patterns   : list        # pola yang terdeteksi, untuk logging
    detail     : dict        # info numerik untuk debug

# ── Fungsi utama ──────────────────────────────────────────────────────────
def layer3_analyze(emotion_history: list) -> Layer3Result:
    """
    Analisis riwayat distress_score dari EmotionResult history.

    Args:
        emotion_history: List EmotionResult dari S2 (urutan kronologis).
                         Setiap item harus punya atribut .distress_score (0.0–1.0)

    Returns:
        Layer3Result dengan skor kontribusi dan pola yang terdeteksi.
    """
    # Butuh minimal 2 data point untuk analisis apapun
    if len(emotion_history) < 2:
        return Layer3Result(score=0.0, patterns=[], detail={"n": len(emotion_history)})

    scores = [e.distress_score for e in emotion_history]
    n      = len(scores)
    latest = scores[-1]

    patterns   = []
    components = {}

    # ── Pola 1: Tren naik konsisten ───────────────────────────────────────
    # Distress naik terus selama minimal TREND_MIN_POINTS pesan berturut-turut.
    # Ini sinyal paling kuat karena menunjukkan kondisi yang aktif memburuk.
    trend_score = 0.0
    if n >= TREND_MIN_POINTS:
        window = scores[-TREND_MIN_POINTS:]
        if all(window[i] < window[i+1] for i in range(len(window)-1)):
            # Hitung steepness: semakin curam, semakin berbahaya
            total_rise = window[-1] - window[0]
            trend_score = min(0.35, total_rise * 0.8)
            patterns.append(f"tren_naik_{TREND_MIN_POINTS}pesan")
            components["trend_rise"] = round(total_rise, 3)

        # Cek window lebih panjang jika ada cukup data (5+ pesan)
        elif n >= 5:
            window5 = scores[-5:]
            if all(window5[i] < window5[i+1] for i in range(4)):
                total_rise = window5[-1] - window5[0]
                trend_score = min(0.40, total_rise * 1.0)
                patterns.append("tren_naik_5pesan")
                components["trend_rise"] = round(total_rise, 3)

    # ── Pola 2: Spike tiba-tiba ───────────────────────────────────────────
    # Kenaikan distress > SPIKE_DELTA dalam satu pesan.
    # Bisa menandakan kejadian traumatis mendadak atau breaking point.
    spike_score = 0.0
    if n >= 2:
        delta = scores[-1] - scores[-2]
        if delta >= SPIKE_DELTA:
            spike_score = min(0.25, delta * 0.6)
            patterns.append(f"spike_{delta:.2f}")
            components["spike_delta"] = round(delta, 3)

    # ── Pola 3: Distress tinggi berkepanjangan ────────────────────────────
    # Stuck di atas HIGH_DISTRESS_THR selama HIGH_DISTRESS_MIN pesan berturut.
    # Sinyal exhaustion — user tidak bisa recover.
    sustained_score = 0.0
    if n >= HIGH_DISTRESS_MIN:
        recent = scores[-HIGH_DISTRESS_MIN:]
        if all(s >= HIGH_DISTRESS_THR for s in recent):
            avg_distress = sum(recent) / len(recent)
            sustained_score = min(0.30, (avg_distress - HIGH_DISTRESS_THR) * 1.5 + 0.10)
            patterns.append(f"distress_tinggi_{HIGH_DISTRESS_MIN}pesan")
            components["sustained_avg"] = round(avg_distress, 3)

    # ── Pola 4: Exhaustion pattern ────────────────────────────────────────
    # Distress sempat turun (user merasa sedikit lebih baik) lalu naik
    # lebih tinggi dari sebelumnya. Ini pola yang sering mendahului krisis.
    # Contoh: [0.4, 0.7, 0.5, 0.8] — turun di tengah tapi akhirnya lebih tinggi
    exhaustion_score = 0.0
    if n >= 4:
        prev_peak = max(scores[-4:-2])
        mid_val   = min(scores[-4:-1])
        current   = scores[-1]
        dip       = prev_peak - mid_val

        if dip >= EXHAUSTION_DROP and current > prev_peak:
            exhaustion_score = min(0.20, (current - prev_peak) * 0.7 + 0.08)
            patterns.append("exhaustion_pattern")
            components["prev_peak"]  = round(prev_peak, 3)
            components["dip"]        = round(dip, 3)
            components["new_peak"]   = round(current, 3)

    # ── Pola 5: Rapid decline pattern ─────────────────────────────────────────
    # Ketika user kayak "relief" dulu (distress turun), tapi kemudian spike ke
    # level lebih tinggi dari peak sebelumnya. Ini pola berbahaya — user udah
    # "give up" setelah mencoba.
    # Contoh: [0.7, 0.5, 0.8] — nunggu untuk apa jika stress bakal naik lagi?
    rapid_relief_score = 0.0
    if n >= 3:
        # Cari moment dimana ada drop, lalu spike lagi
        for i in range(1, n - 1):
            prev = scores[i-1]
            current = scores[i]
            next_score = scores[i+1]

            dip = prev - current
            rise_after = next_score - current

            # Ada relief (dip >= threshold) lalu spike lagi
            if dip >= EXHAUSTION_DROP and rise_after >= 0.20 and next_score >= prev:
                rapid_relief_score = min(0.25, dip * 0.6 + rise_after * 0.8)
                patterns.append("rapid_relief_then_spike")
                components["relief_dip"] = round(dip, 3)
                components["spike_after"] = round(rise_after, 3)
                break  # Hanya ambil satu instance

    # ── Pola 5b: Distress tinggi pada pesan terakhir saja (fallback) ────────
    # Fallback ringan — jika tidak ada pola di atas tapi distress terakhir
    # memang tinggi, tetap kasih sedikit kontribusi.
    latest_score = 0.0
    if not patterns and latest >= HIGH_DISTRESS_THR:
        latest_score = min(0.15, (latest - HIGH_DISTRESS_THR) * 0.5)
        patterns.append(f"distress_latest_{latest:.2f}")

    # ── Gabungkan (ambil yang tertinggi, bukan dijumlah) ──────────────────
    # Alasan: pola-pola ini sering overlap (tren naik + spike bisa terjadi
    # bersamaan). Menjumlah akan double-count. Ambil tertinggi + bonus kecil
    # jika ada multiple pattern.
    component_scores = [trend_score, spike_score, sustained_score,
                        exhaustion_score, rapid_relief_score, latest_score]
    base_score = max(component_scores)

    # Bonus jika ada 2+ pola berbeda terdeteksi bersamaan
    n_patterns = sum(1 for s in component_scores if s > 0)
    bonus = 0.05 * max(0, n_patterns - 1)

    final_score = min(0.40, base_score + bonus)

    return Layer3Result(
        score=round(final_score, 4),
        patterns=patterns,
        detail={
            "n_history"      : n,
            "latest_distress": round(latest, 3),
            "scores_last5"   : [round(s, 3) for s in scores[-5:]],
            "components"     : components,
            "base_score"     : round(base_score, 4),
            "bonus"          : round(bonus, 4),
        }
    )


# ── Quick test ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    from dataclasses import dataclass as dc

    @dc
    class MockEmotion:
        distress_score: float

    scenarios = [
        {
            "name"    : "Normal — tidak ada pola berbahaya",
            "scores"  : [0.2, 0.3, 0.25, 0.2],
            "expected": "NORMAL",
        },
        {
            "name"    : "Tren naik konsisten (3 pesan)",
            "scores"  : [0.3, 0.5, 0.72],
            "expected": "L2+",
        },
        {
            "name"    : "Tren naik konsisten (5 pesan)",
            "scores"  : [0.2, 0.35, 0.50, 0.65, 0.80],
            "expected": "L3",
        },
        {
            "name"    : "Spike tiba-tiba",
            "scores"  : [0.2, 0.25, 0.20, 0.65],
            "expected": "L2",
        },
        {
            "name"    : "Distress tinggi berkepanjangan",
            "scores"  : [0.3, 0.70, 0.72, 0.68, 0.75],
            "expected": "L2+",
        },
        {
            "name"    : "Exhaustion pattern",
            "scores"  : [0.4, 0.72, 0.50, 0.85],
            "expected": "L2+",
        },
        {
            "name"    : "Tren naik + spike (multi-pattern)",
            "scores"  : [0.25, 0.40, 0.55, 0.88],
            "expected": "L3",
        },
    ]

    print("=" * 60)
    print("CDS Layer 3 — History Trend Analysis Test")
    print("=" * 60)

    for s in scenarios:
        history = [MockEmotion(distress_score=v) for v in s["scores"]]
        result  = layer3_analyze(history)

        if   result.score >= 0.30: level = "L3"
        elif result.score >= 0.20: level = "L2+"
        elif result.score >= 0.10: level = "L2"
        elif result.score >  0.0 : level = "L1"
        else:                      level = "NORMAL"

        ok   = level == s["expected"]
        icon = "PASS" if ok else "FAIL"

        print(f"\n{icon} {s['name']}")
        print(f"   Scores   : {s['scores']}")
        print(f"   L3 Score : {result.score:.4f}  → {level} (expected: {s['expected']})")
        print(f"   Patterns : {result.patterns if result.patterns else '—'}")