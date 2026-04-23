# s4_summary/summary_generator.py
# S4 — Session Summary Generator

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from uuid import uuid4

FLAG_LOW    = "LOW"
FLAG_MEDIUM = "MEDIUM"
FLAG_HIGH   = "HIGH"

@dataclass
class SessionSummary:
    paragraf        : str
    flag            : str
    flag_reasoning  : str
    pesan_penutup   : str
    cds_level_akhir : str
    distress_awal   : float
    distress_akhir  : float
    tren_distress   : str
    jumlah_pesan    : int
    raw_json        : dict = field(default_factory=dict)
    session_id      : str  = ""  # NEW: unique session ID
    session_file    : str  = ""  # NEW: path to saved JSON file


# ── Direktori penyimpanan sesi ─────────────────────────────────────────────
SESSION_DIR = Path(__file__).parent.parent / "data" / "sessions"


def save_session_json(
    session_id      : str,
    chat_log        : list,
    emotion_history : list,
    summary         : "SessionSummary",
) -> str:
    """
    Simpan data sesi ke JSON sementara di data/sessions/.
    Dipanggil otomatis saat generate_summary() selesai.

    Returns:
        Path lengkap file yang disimpan.
    """
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    filepath = SESSION_DIR / f"{session_id}.json"

    emotion_timeline = [
        {
            "dominant"      : e.dominant,
            "score"         : round(e.score, 4),
            "distress_score": round(e.distress_score, 4),
            "topics"        : e.topics,
        }
        for e in emotion_history
    ]

    payload = {
        "session_id"      : session_id,
        "timestamp"       : datetime.now().isoformat(),
        "flag"            : summary.flag,
        "flag_reasoning"  : summary.flag_reasoning,
        "tren_distress"   : summary.tren_distress,
        "distress_awal"   : summary.distress_awal,
        "distress_akhir"  : summary.distress_akhir,
        "cds_level_akhir" : summary.cds_level_akhir,
        "jumlah_pesan"    : summary.jumlah_pesan,
        "ringkasan"       : summary.paragraf,
        "pesan_penutup"   : summary.pesan_penutup,
        "chat_log"        : chat_log,
        "emotion_timeline": emotion_timeline,
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    return str(filepath)


def delete_session_json(session_file: str) -> bool:
    """
    Hapus file JSON sesi — dipanggil jika user menolak referral ke psikolog.

    Returns:
        True jika berhasil dihapus, False jika file tidak ditemukan.
    """
    try:
        path = Path(session_file)
        if path.exists():
            path.unlink()
            return True
        return False
    except Exception:
        return False


def _compute_flag(cds_level: str, distress_akhir: float, tren: str) -> str:
    if cds_level == "L3":
        return FLAG_HIGH
    if cds_level == "L2" or distress_akhir >= 0.70:
        if tren == "memburuk" and distress_akhir >= 0.65:
            return FLAG_HIGH
        return FLAG_MEDIUM
    if cds_level == "L1" or distress_akhir >= 0.50:
        return FLAG_MEDIUM
    return FLAG_LOW


# ── System prompt ─────────────────────────────────────────────────────────
SUMMARY_SYSTEM_PROMPT = """
Kamu Karuna, AI pendengar empatik yang baru saja menyelesaikan sesi percakapan.
Tugasmu: buat ringkasan sesi yang INFORMATIF, spesifik, dan berempati dalam JSON.

═══════════════════════════════════════════════════════════
ATURAN KETAT: ANTI-TERCAMPUR SESI
═══════════════════════════════════════════════════════════
✓ Hanya rujuk isi TRANSKRIP SESI yang diberikan.
✗ JANGAN bawa detail, nama, atau peristiwa dari sesi lain.
✗ Jika data tidak ada → jangan asumsikan.
✓ Echo session_id persis sama dengan input.

═══════════════════════════════════════════════════════════
INSTRUKSI "paragraf" — NARATIF INFORMATIF & KOMPREHENSIF
═══════════════════════════════════════════════════════════

Tulis 5-8 kalimat yang WAJIB mencakup semua aspek ini:

1. EMOSI OVERALL — Gambaran lengkap lanskap emosional user.
   • Emosi apa saja yang muncul? Bagaimana intensitasnya?
   • Apakah ada pergeseran emosi selama percakapan? Dari apa ke apa?
   • Mana emosi yang paling dominan/mendalam?
   ✓ "Sepanjang percakapan, emosi user bergerak dari kemarahan yang pekat
      terhadap ayahnya, menuju kesedihan yang lebih dalam saat menyentuh
      rasa tidak berharga. Di akhir, muncul kelelahan emosional yang kuat —
      seolah energi untuk marah pun sudah habis."
   ✗ "User merasa sedih dan marah." — TERLALU DANGKAL.

2. MASALAH INTI — Akar permasalahan yang sebenarnya dihadapi user.
   • Bukan hanya situasi permukaan, tapi apa yang SESUNGGUHNYA menyakitkan.
   • Identifikasi masalah utama vs masalah turunan.
   ✓ "Masalah intinya bukan soal nilai ujian yang jelek — tapi rasa
      bahwa apapun yang dia lakukan tidak pernah cukup di mata ayahnya.
      Ini menciptakan keyakinan mendalam bahwa dia 'cacat' dan tidak layak."
   ✗ "Dia punya masalah dengan keluarga." — TERLALU ABSTRAK.

3. KONTEKS SITUASI — Apa yang user alami/ceritakan secara konkret?
   ✓ Spesifik: kejadian, orang, tempat, waktu yang disebut user.
   ✓ "Ayahnya memukul karena nilai ujian, lalu mengatakan 'harusnya kamu
      gak usah lahir'. Ini terjadi rutin sejak SD."

4. PIKIRAN & POLA INTERNAL — Cara berpikir user yang terlihat.
   ✓ "User menyalahkan diri sendiri, punya pola 'seharusnya aku bisa' yang berulang."
   ✗ JANGAN diagnosa klinis ("obsessive", "depressive thinking").
   PENTING: JIKA ADA SINYAL PIKIRAN BUNUH DIRI / MENYAKITI DIRI:
      Sebutkan JELAS dengan bahasa empatik, bukan klinis.

5. KEBUTUHAN USER — Apa yang tampak dibutuhkan?
   ✓ Dari ucapan eksplisit atau tersirat: "User butuh validasi bahwa
      perasaan marahnya wajar, dan butuh tahu ada orang yang benar-benar mendengar."

TONE:
Catatan seseorang yang hadir dan benar-benar mendengarkan — bukan laporan klinis.
Bahasa hangat, informal Indonesia. JANGAN label diagnosis.
Paragraf harus cukup informatif sehingga seseorang yang TIDAK membaca transkrip
bisa memahami apa yang user rasakan, masalah utamanya, dan kondisi emosionalnya.

═══════════════════════════════════════════════════════════
INSTRUKSI "flag"
═══════════════════════════════════════════════════════════
Gunakan flag sistem sebagai MINIMUM (jangan turunkan).
Boleh NAIKKAN jika ada sinyal lebih serius di transkrip.

LOW    = tidak ada sinyal klinis atau distress signifikan
MEDIUM = ada tekanan/distress yang perlu perhatian; disarankan konsultasi
HIGH   = sinyal distress/krisis kuat ATAU ada pikiran menyakiti diri

═══════════════════════════════════════════════════════════
INSTRUKSI "flag_reasoning"
═══════════════════════════════════════════════════════════
1-2 kalimat spesifik kenapa flag ini.
Fokus pada bukti dari percakapan — konkret, bukan generik.

✓ HIGH: "User menyebut pikiran ingin mengakhiri hidup, merasa putus asa
       total, dan tidak melihat jalan keluar apapun."
✗ HIGH: "User sangat tertekan dan membutuhkan bantuan profesional."

═══════════════════════════════════════════════════════════
INSTRUKSI "pesan_penutup"
═══════════════════════════════════════════════════════════
2-3 kalimat yang:
• ACKNOWLEDGE perasaan mereka — spesifik ke cerita, bukan generic
• Validasi keberanian mereka berbagi
• JIKA flag MEDIUM/HIGH: dengan lembut mention bantuan profesional
• Hangat, personal, tulus

✓ "Terima kasih sudah percaya cerita itu ke aku. Aku ngerti lo
  cuma pengen didengar. Ada yang bisa membantu kalau lo mau ngomong
  lebih lanjut."

✗ "Terima kasih sudah menceritakan masalahmu. Aku ada untuk membantu."

═══════════════════════════════════════════════════════════
OUTPUT: JSON VALID
═══════════════════════════════════════════════════════════
{
    "session_id_echo": "<HARUS SAMA DENGAN session_id INPUT>",
    "paragraf": "...",
    "flag": "LOW" | "MEDIUM" | "HIGH",
    "flag_reasoning": "...",
    "pesan_penutup": "..."
}
"""


def _build_summary_prompt(
    session_id      : str,
    chat_log        : list,
    emotion_history : list,
    cds_level       : str,
    system_flag     : str,
) -> str:
    user_turns = [msg["content"] for msg in chat_log if msg.get("role") == "user"]

    lines = []
    for i, msg in enumerate(chat_log, start=1):
        role = "User" if msg["role"] == "user" else "Karuna"
        lines.append(f"[{i:02d}] {role}: {msg['content']}")
    chat_text = "\n".join(lines)

    # Ambil kutipan user yang paling informatif (bukan hanya terakhir 6)
    # Prioritaskan quotes yang panjang dan emosional
    key_user_quotes = []
    for u in user_turns:
        if len(u) > 50 or any(marker in u for marker in ["gak", "udah", "ya", "masih", "mau"]):
            key_user_quotes.append(u)

    # Ambil sampel unik, max 8 quotes
    user_focus = "\n".join(f"- {repr(u)}" for u in key_user_quotes[-8:]) if key_user_quotes else "- (tidak ada)"

    if emotion_history:
        emosi_per_pesan = []
        for i, e in enumerate(emotion_history):
            emosi_per_pesan.append(
                f"  Msg{i+1}: {e.dominant} (conf={e.score:.0%}), "
                f"distress={e.distress_score:.0%}, topik={','.join(e.topics)}"
            )
        distress_list = [round(e.distress_score, 2) for e in emotion_history]

        # Compute trend
        if len(distress_list) >= 2:
            delta = distress_list[-1] - distress_list[0]
            trend_text = "naik" if delta > 0.1 else "turun" if delta < -0.1 else "stabil"
        else:
            trend_text = "single_msg"

        # Compute emotion distribution across session
        emotion_counts = {}
        for e in emotion_history:
            emotion_counts[e.dominant] = emotion_counts.get(e.dominant, 0) + 1
        emotion_summary = ", ".join(
            f"{emo}({cnt}x)" for emo, cnt in
            sorted(emotion_counts.items(), key=lambda x: -x[1])
        )

        # Collect all unique topics
        all_topics = []
        for e in emotion_history:
            for t in e.topics:
                if t not in all_topics:
                    all_topics.append(t)

        stats = (
            f"EMOSI & DISTRESS PER PESAN:\n" + "\n".join(emosi_per_pesan) + "\n"
            f"\nEMOSI OVERALL SESI: {emotion_summary}\n"
            f"TOPIK YANG MUNCUL: {', '.join(all_topics) if all_topics else '—'}\n"
            f"Distress trajectory: {distress_list}\n"
            f"Trend: {trend_text} ({distress_list[-1] - distress_list[0]:+.2f})\n"
            f"CDS level akhir: {cds_level}\n"
            f"Flag minimum sistem: {system_flag}\n\n"
            f"INSTRUKSI TAMBAHAN: Gunakan data emosi di atas untuk menggambarkan\n"
            f"perjalanan emosional user secara detail dalam paragraf. Sebutkan\n"
            f"masalah INTI yang user hadapi (bukan hanya permukaan). Paragraf harus\n"
            f"cukup informatif sehingga pembaca bisa memahami kondisi user tanpa\n"
            f"membaca transkrip."
        )
    else:
        stats = f"CDS level akhir: {cds_level}\nFlag minimum sistem: {system_flag}"

    return (
        f"=== BATAS SESI ===\n"
        f"session_id: {session_id}\n"
        "PENTING: Gunakan HANYA data dalam blok ini. Abaikan ingatan dari sesi lain.\n\n"
        f"=== KUTIPAN USER (sampling key quotes) ===\n{user_focus}\n\n"
        f"=== TRANSKRIP LENGKAP ===\n{chat_text}\n\n"
        f"=== DATA EMOSI & SISTEM ===\n{stats}\n\n"
        "Buat ringkasan sesi dalam JSON. Paragraf harus spesifik ke cerita user, "
        "jangan generic. Acknowledge emosi mereka dengan detail konkret dari transkrip. "
        "Echo session_id persis sama dengan nilai di atas."
    )


def _extract_json(raw: str) -> dict:
    """
    Robust JSON extraction — 5-layer fallback untuk semua variasi output LLM.
    """
    text = re.sub(r"```json\s*|\s*```", "", raw).strip()

    # Layer 1: direct parse
    try:
        return json.loads(text)
    except Exception:
        pass

    # Layer 2: find outermost { }
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass

    # Layer 3: fix trailing commas
    cleaned = re.sub(r",\s*([}\]])", r"\1", text)
    try:
        return json.loads(cleaned)
    except Exception:
        pass

    # Layer 4: single to double quote (apostrophe-safe)
    try:
        fixed = re.sub(r"(?<![a-zA-Z])'([^']*)'(?=[:\s,}\]])", r'"\1"', text)
        return json.loads(fixed)
    except Exception:
        pass

    # Layer 5: manual regex extraction per field
    result = {}
    for field in ["session_id_echo", "paragraf", "flag", "flag_reasoning", "pesan_penutup"]:
        pattern = '"'  + field + '"\\s*:\\s*"((?:[^"\\\\]|\\\\.)*)"\\s*[,}]'
        m = re.search(pattern, text, re.DOTALL)
        if m:
            result[field] = m.group(1).replace('\\"', '"')
    if result.get("paragraf"):
        return result

    return {}

def generate_summary(
    chat_log        : list,
    emotion_history : list,
    cds_level       : str,
) -> SessionSummary:
    from s1_conversational.groq_client import generate_content_safe, DEFAULT_MODEL

    # ID berbasis waktu + random suffix agar aman saat banyak user menutup sesi bersamaan.
    session_id = f"karuna_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}_{uuid4().hex[:8]}"

    distress_awal  = emotion_history[0].distress_score  if emotion_history else 0.0
    distress_akhir = emotion_history[-1].distress_score if emotion_history else 0.0
    delta = distress_akhir - distress_awal

    if   delta <= -0.10: tren = "membaik"
    elif delta >=  0.10: tren = "memburuk"
    else:                tren = "stabil"

    system_flag = _compute_flag(cds_level, distress_akhir, tren)
    prompt_user = _build_summary_prompt(session_id, chat_log, emotion_history, cds_level, system_flag)

    data = {}
    last_error = None

    # Retry hingga 3x jika Groq gagal
    for attempt in range(3):
        try:
            raw_text = generate_content_safe(
                model=DEFAULT_MODEL,
                system_prompt=SUMMARY_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt_user}],
                max_tokens=1500,
                temperature=0.3,
            )
            raw_text = raw_text.strip() if raw_text else ""

            if not raw_text:
                last_error = ValueError(f"Groq returned empty response (attempt {attempt+1})")
                print(f"[S4] Attempt {attempt+1}: Groq returned empty text")
                continue

            data = _extract_json(raw_text)

            if not data.get("paragraf"):
                last_error = ValueError(f"JSON parse ok but no 'paragraf' field (attempt {attempt+1})")
                print(f"[S4] Attempt {attempt+1}: JSON parsed but missing 'paragraf'. Keys: {list(data.keys())}")
                data = {}
                continue

            # session_id_echo: log mismatch as warning, tapi JANGAN gagalkan
            # Groq sering tidak echo persis — yang penting paragraf ada
            echoed = data.get("session_id_echo", "")
            if echoed != session_id:
                print(f"[S4] session_id_echo mismatch (expected={session_id[:30]}..., got={str(echoed)[:30]}...) — tetap diterima")
                data["session_id_echo"] = session_id  # force-correct

            # Sukses
            break

        except Exception as e:
            last_error = e
            print(f"[S4] Attempt {attempt+1} exception: {type(e).__name__}: {e}")

    # Fallback jika semua attempt gagal
    if not data.get("paragraf"):
        print(f"[S4] All attempts failed. Last error: {last_error}. Building fallback summary.")
        # Buat fallback yang lebih informatif dari data S2/S3 yang sudah ada
        user_msgs = [m["content"] for m in chat_log if m["role"] == "user"]
        topik_hint = ""
        emosi_hint = ""
        if emotion_history:
            # Collect topics
            topik_set = []
            for e in emotion_history:
                for t in e.topics:
                    if t not in topik_set:
                        topik_set.append(t)
            if topik_set:
                topik_hint = f" Topik yang dibicarakan: {', '.join(topik_set)}."

            # Collect emotion distribution
            emo_counts = {}
            for e in emotion_history:
                emo_counts[e.dominant] = emo_counts.get(e.dominant, 0) + 1
            emo_desc = ", ".join(
                f"{emo} ({cnt}x)" for emo, cnt in
                sorted(emo_counts.items(), key=lambda x: -x[1])
            )
            emosi_hint = f" Emosi yang terdeteksi sepanjang sesi: {emo_desc}."

        # Determine narrative based on distress trend
        if len(emotion_history) > 1:
            trend_desc = tren.capitalize()
        else:
            trend_desc = "Satu percakapan singkat"

        data = {
            "session_id_echo": session_id,
            "paragraf": (
                f"Dalam sesi ini user berbagi perasaan mereka.{emosi_hint}{topik_hint} "
                f"Tren distress: {trend_desc} (awal: {distress_awal:.0%}, akhir: {distress_akhir:.0%}). "
                f"CDS level tercatat: {cds_level}."
                f"{' Meskipun demikian, ada poin-poin penting yang perlu diperhatikan.' if cds_level != 'NORMAL' else ''} "
                f"Ringkasan otomatis tidak tersedia karena kendala teknis — mohon review transkrip chat secara manual."
            ),
            "flag"          : system_flag,
            "flag_reasoning": (
                f"Flag {system_flag} berdasarkan CDS level {cds_level}, distress akhir {distress_akhir:.0%}, "
                f"dan tren {tren}. Review manual transkrip disarankan."
            ),
            "pesan_penutup" : (
                f"Terima kasih sudah berbagi hari ini — itu membutuhkan keberanian{' dan kepercayaan.' if len(user_msgs) > 1 else '.'} "
                f"Karuna selalu ada kalau kamu mau ngobrol lagi."
            ),
        }

    # Pastikan flag tidak di bawah system_flag
    FLAG_ORDER = {FLAG_LOW: 0, FLAG_MEDIUM: 1, FLAG_HIGH: 2}
    llm_flag = str(data.get("flag", system_flag)).upper()
    if llm_flag not in FLAG_ORDER:
        llm_flag = system_flag
    if FLAG_ORDER.get(llm_flag, 0) < FLAG_ORDER[system_flag]:
        data["flag"] = system_flag
    else:
        data["flag"] = llm_flag

    data["session_id_echo"] = session_id

    summary = SessionSummary(
        paragraf        = data.get("paragraf", "—"),
        flag            = data["flag"],
        flag_reasoning  = data.get("flag_reasoning", "—"),
        pesan_penutup   = data.get("pesan_penutup", ""),
        cds_level_akhir = cds_level,
        distress_awal   = round(distress_awal, 3),
        distress_akhir  = round(distress_akhir, 3),
        tren_distress   = tren,
        jumlah_pesan    = len([m for m in chat_log if m["role"] == "user"]),
        raw_json        = data,
        session_id      = session_id,
    )

    # Auto-save JSON sementara — user akan diminta konfirmasi referral di UI
    session_file = save_session_json(session_id, chat_log, emotion_history, summary)
    summary.session_file = session_file

    return summary