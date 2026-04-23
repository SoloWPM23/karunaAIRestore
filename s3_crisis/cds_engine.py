# s3_crisis/cds_engine.py
# Crisis Detection System — orchestrator Layer 1 + Layer 2 + Layer 3
#
# Alur deteksi:
#
#   Teks masuk
#      │
#      ├─▶ [Layer 1] Keyword/regex      ──── < 5ms
#      │       └── L3 eksplisit → fast-path return L3
#      │
#      ├─▶ [Layer 2] IndoBERT           ──── < 300ms
#      │       └── Deteksi krisis implisit dari konten teks
#      │
#      ├─▶ [Layer 3] History Trend      ──── < 5ms
#      │       └── Deteksi pola memburuk dari riwayat distress_score
#      │
#      └─▶ [Engine] Gabungkan L1+L2+L3  ──── < 1ms
#              └── level final: NORMAL / L1 / L2 / L3

from dataclasses import dataclass, field
from s3_crisis.cds_layer1 import layer1_detect
from s3_crisis.cds_layer2 import layer2_detect
from s3_crisis.cds_layer3 import layer3_analyze

# ── Output utama ───────────────────────────────────────────────────────────
@dataclass
class CDSResult:
    level    : str         # "NORMAL" / "L1" / "L2" / "L3"
    score    : float       # skor gabungan 0.0 – 1.0
    triggers : list        # sumber deteksi, untuk logging/debug
    detail   : dict = field(default_factory=dict)

# ── Bobot penggabungan L1 + L2 + L3 ──────────────────────────────────────
# L3 mengisi slot W_HISTORY yang sebelumnya dipakai hist_score sederhana.
# L3 tidak boleh terlalu dominan — dia penguat, bukan penentu utama.
W_LAYER1 = 0.45
W_LAYER2 = 0.40
W_LAYER3 = 0.15

# Mapping level → skor numerik
LEVEL_SCORE = {
    "NORMAL": 0.05,
    "L1":     0.35,
    "L2":     0.65,
    "L3":     0.92,
}

# ── Fungsi utama ───────────────────────────────────────────────────────────
def analyze_crisis(text: str, emotion_history: list = []) -> CDSResult:
    """
    Analisis teks dan riwayat emosi, kembalikan level krisis beserta skornya.

    Args:
        text           : Pesan terbaru dari user
        emotion_history: List EmotionResult dari S2 (urutan kronologis).
                         Setiap item harus punya atribut .distress_score

    Returns:
        CDSResult dengan level, score, triggers, dan detail semua layer
    """

    # ── Layer 1: Keyword / Regex ──────────────────────────────────────────
    level_l1, conf_l1 = layer1_detect(text)

    # Fast-path: keyword L3 eksplisit → langsung return, skip L2 dan L3
    if level_l1 == "L3":
        return CDSResult(
            level="L3",
            score=0.95,
            triggers=["L1_keyword_L3"],
            detail={
                "l1_level"  : "L3",
                "l1_conf"   : conf_l1,
                "l2_skipped": True,
                "l3_skipped": True,
            }
        )

    # ── Layer 2: IndoBERT ─────────────────────────────────────────────────
    l2_result = layer2_detect(text)
    level_l2  = l2_result.level
    conf_l2   = l2_result.confidence

    # ── Layer 3: History Trend Analysis ──────────────────────────────────
    l3_result = layer3_analyze(emotion_history)

    # ── Penggabungan skor ─────────────────────────────────────────────────
    score_l1 = LEVEL_SCORE[level_l1] * conf_l1
    score_l2 = LEVEL_SCORE[level_l2] * conf_l2
    score_l3 = l3_result.score       # sudah dalam skala 0.0–0.40

    final_score = (
        score_l1 * W_LAYER1 +
        score_l2 * W_LAYER2 +
        score_l3 * W_LAYER3
    )

    # ── Override 1: L2 yakin krisis → eskalasi level ─────────────────────
    # Tiga skenario:
    #
    # a) L2 crisis + L1 deteksi sesuatu → dua sinyal setuju → L3
    #    Contoh: "mau mengakhiri semuanya" + keyword L2
    #
    # b) L2 crisis + L1 NORMAL + distress tinggi (>=0.55) + conf sangat tinggi (>=0.93)
    #    → satu sinyal tapi diperkuat S2 → maksimal L2
    #    Contoh: "semua lebih baik tanpa gue" — implisit kuat, distress tinggi
    #
    # c) L2 crisis + L1 NORMAL + distress rendah + tidak ada tren L3
    #    → false positive (OOD); redam skor ke NORMAL
    #    Contoh: "halo, apa kabar?" — sapaan biasa, tidak ada sinyal lain
    latest_distress = (
        emotion_history[-1].distress_score if emotion_history else 0.0
    )
    _l2_fp_suppressed = False   # flag: apakah L2 ditekan sebagai false positive

    if l2_result.label == "crisis" and conf_l2 >= 0.92:
        if level_l1 != "NORMAL":
            final_score = max(final_score, 0.75)            # skenario (a) → L3
        elif latest_distress >= 0.55 and conf_l2 >= 0.93:
            final_score = max(final_score, 0.45)            # skenario (b) → L2
        elif latest_distress < 0.55 and l3_result.score < 0.10:
            # skenario (c): tidak ada sinyal lain, kemungkinan besar false positive
            # Batasi skor ke bawah ambang L1 agar hasilnya NORMAL
            final_score = min(final_score, 0.19)
            _l2_fp_suppressed = True

    # ── Override 2: L3 tren parah + L2 at_risk → eskalasi ke L2 minimum ─
    # Tren memburuk konsisten harus minimal L2 meski konten satu pesan
    # terakhir terdengar biasa saja
    if l3_result.score >= 0.25 and l2_result.label in ("at_risk", "crisis"):
        final_score = max(final_score, 0.45)

    # ── Tentukan level final ──────────────────────────────────────────────
    if   final_score >= 0.75: level = "L3"
    elif final_score >= 0.45: level = "L2"
    elif final_score >= 0.20: level = "L1"
    else:                     level = "NORMAL"

    # ── Kumpulkan triggers ────────────────────────────────────────────────
    triggers = []
    if level_l1 != "NORMAL":
        triggers.append(f"L1_keyword_{level_l1}")
    if l2_result.label != "safe" and not _l2_fp_suppressed:
        triggers.append(f"L2_model_{l2_result.label}")
    if l3_result.patterns:
        for p in l3_result.patterns:
            triggers.append(f"L3_{p}")
    if not triggers:
        triggers.append("none")

    return CDSResult(
        level=level,
        score=round(final_score, 4),
        triggers=triggers,
        detail={
            # Layer 1
            "l1_level"    : level_l1,
            "l1_conf"     : conf_l1,
            # Layer 2
            "l2_label"    : l2_result.label,
            "l2_level"    : level_l2,
            "l2_conf"     : round(conf_l2, 4),
            "l2_probs"    : l2_result.probs,
            # Layer 3
            "l3_score"    : l3_result.score,
            "l3_patterns" : l3_result.patterns,
            "l3_detail"   : l3_result.detail,
            # Skor per layer (untuk transparansi)
            "score_l1"    : round(score_l1, 4),
            "score_l2"    : round(score_l2, 4),
            "score_l3"    : round(score_l3, 4),
            "final_score" : round(final_score, 4),
        }
    )


# ── Quick test ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    from dataclasses import dataclass as dc

    @dc
    class MockEmotion:
        distress_score: float

    basic_cases = [
        ("hari ini seru banget abis makan sama temen",            [],                                                          "NORMAL"),
        ("gue lagi capek banget sama kerjaan",                    [],                                                          "NORMAL"),
        ("gue mau bunuh diri, udah gak kuat",                     [],                                                          "L3"),
        ("semua orang bakal lebih baik tanpa gue ada",            [],                                                          "L3"),
        ("udah lama gue ngerasa gak ada gunanya buat terus coba", [],                                                          "L2"),
    ]

    trending_cases = [
        (
            "hari ini biasa aja sih",
            [MockEmotion(0.30), MockEmotion(0.45), MockEmotion(0.62), MockEmotion(0.78)],
            "L2",
        ),
        (
            "gue udah gak tau lagi",
            [MockEmotion(0.25), MockEmotion(0.40), MockEmotion(0.60), MockEmotion(0.80)],
            "L3",
        ),
    ]

    all_cases = basic_cases + trending_cases

    print("=" * 65)
    print("CDS Engine — Integration Test (Layer 1 + 2 + 3)")
    print("=" * 65)

    correct = 0
    for text, history, expected in all_cases:
        result  = analyze_crisis(text, history)
        ok      = result.level == expected
        correct += int(ok)
        icon    = "PASS" if ok else "FAIL"

        print(f"\n{icon} [{result.level:6s}] {text[:52]}")
        print(f"     Expected  : {expected}")
        print(f"     Score     : {result.score:.4f} | Triggers: {result.triggers}")

        d = result.detail
        if d.get("l2_skipped"):
            print(f"     L1        : L3 keyword — L2/L3 di-skip")
        else:
            print(f"     L1        : {d['l1_level']} ({d['l1_conf']:.2f})"
                  f"  score={d['score_l1']:.4f}")
            print(f"     L2        : {d['l2_label']} / {d['l2_level']}"
                  f" (conf={d['l2_conf']:.3f})  score={d['score_l2']:.4f}")
            l3p = d['l3_patterns'] if d['l3_patterns'] else "—"
            print(f"     L3        : {l3p}  score={d['score_l3']:.4f}")

    print(f"\n{'='*65}")
    print(f"Hasil: {correct}/{len(all_cases)} benar")