# s1_conversational/output_validator.py

import re

# ── Kata/frasa yang TIDAK boleh ada di respons ────────────────────────────
FORBIDDEN = [
    r"\b(depresi|bipolar|skizofrenia|anxietas|ptsd)\b",   # label diagnosis
    r"\b(obat|dosis|resep|mg|antidepresan)\b",            # saran medis
    r"\b(semangat ya|pasti bisa|kamu kuat)\b",            # toxic positivity
    r"\bseharusnya kamu\b",
    r"\bsetidaknya\b",
    r"\baku bisa (ngebayangin|membayangkan)\b",           # generic empathy filler
]

# ── Respons krisis darurat — bypass cek open-ended ────────────────────────
# Saat CDS level L3, LLM akan mengarahkan user ke hotline.
# Respons seperti ini VALID meski tidak ada kalimat tanya — justru
# tidak boleh "mengajak cerita lebih" saat user dalam bahaya akut.
CRISIS_BYPASS_PATTERNS = [
    r"\b(119|into the light|hotline|darurat|segera hubungi|bantuan segera)\b",
    r"\b(profesional|konselor|psikolog|psikiater).{0,30}\b(hubungi|segera|bantu)\b",
]

# ── Frasa open-ended untuk respons non-krisis ─────────────────────────────
OPEN_ENDED_PATTERNS = [
    r"\?",
    r"\.\.\.",
    r"\b(cerita|ceritain|ceritakan)\b",
    r"\b(boleh|mau|ingin|bisa)\b.{0,30}\b(cerita|share|ngobrol|bicara)\b",
    r"\b(aku (di sini|ada|dengarkan|siap))\b",
    r"\b(kalau mau|jika mau|jika ingin|kalau ingin)\b",
    r"\b(gimana|bagaimana).{0,20}\b(perasaan|rasanya|menurutmu)\b",
    r"\b(apa yang|hal apa).{0,30}\b(rasakan|pikirkan)\b",
    r"\baku (dengerin|dengarkan|temani|temeni)\b",
    r"\b(lanjut|terus|lebih lanjut)\b",
    r"\b(tidak sendirian|gak sendirian)\b",   # menegaskan kehadiran
    r"\b(aku (di sampingmu|sama kamu|bareng kamu))\b",
]

def validate(response: str, cds_level: str = "NORMAL") -> tuple[bool, str]:
    """
    Cek apakah respons AI aman dan tepat untuk dikirim ke user.

    Args:
        response : Teks respons dari LLM
        cds_level: Level krisis saat ini ("NORMAL"/"L1"/"L2"/"L3")
                   Jika L3, cek open-ended di-bypass karena respons krisis
                   memang bersifat direktif (arahkan ke hotline).

    Returns:
        (True jika valid, alasan jika tidak valid)
    """
    words = response.split()
    response_lower = response.lower()

    # ── Panjang ───────────────────────────────────────────────────────────
    if len(words) > 150:
        return False, f"Terlalu panjang: {len(words)} kata"
    if len(words) < 10:
        return False, f"Terlalu pendek: {len(words)} kata"

    # ── Kata terlarang ────────────────────────────────────────────────────
    for pattern in FORBIDDEN:
        if re.search(pattern, response_lower):
            matched = re.search(pattern, response_lower).group() # type: ignore
            return False, f"Kata terlarang: '{matched}'"

    # ── Cek open-ended ────────────────────────────────────────────────────
    # Bypass jika: (1) CDS level L3, atau (2) respons mengandung arahan krisis
    is_crisis_response = (
        cds_level == "L3" or
        any(re.search(p, response_lower) for p in CRISIS_BYPASS_PATTERNS)
    )

    if not is_crisis_response:
        has_open_ended = any(
            re.search(p, response_lower) for p in OPEN_ENDED_PATTERNS
        )
        if not has_open_ended:
            return False, "Respons terkesan menutup percakapan"

    return True, "OK"