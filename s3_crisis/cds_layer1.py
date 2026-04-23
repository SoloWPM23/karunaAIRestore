# s3_crisis/cds_layer1.py
# Layer 1 — Keyword & Regex Detection  (<5ms, no ML)
#
# Dua kategori sinyal L3:
#   EKSPLISIT — pernyataan langsung bunuh diri / kematian
#   IMPLISIT  — referensi alat/cara, metafora, frasa tidak langsung
#               yang umum dalam konteks ASEAN/Indonesia

import re

# ── L3 Eksplisit ──────────────────────────────────────────────────────────
KEYWORDS_L3_EKSPLISIT = [
    r"\b(bunuh diri|mau bunuh diri|pengen bunuh diri|ingin bunuh diri)\b",
    r"\b(mau mati|pengen mati|ingin mati|mau mengakhiri hidup)\b",
    r"\b(tidak mau hidup|gak mau hidup|udah gak mau hidup|ga mau hidup lagi)\b",
    r"\b(akhiri hidup|akhiri segalanya|mengakhiri hidup|akhiri semua ini)\b",
    r"\b(mati aja|matiin diri|mati sekalian)\b",
    r"\b(sudah tidak ada gunanya aku|gak ada gunanya lagi hidup)\b",
]

# ── L3 Implisit ───────────────────────────────────────────────────────────
KEYWORDS_L3_IMPLISIT = [
    # Referensi tali — dengan konteks berbahaya (improved context match)
    r"\b(tali).{0,20}(meter|cm|memanggilku|memanggil|gantung|leher|neck)\b",
    r"\b(membeli|beli|punya|ada|siapin|siapkan|udah siapin).{0,15}(tali).{0,40}(mengakhiri|akhiri|bunuh|pergi selamanya|hidup|nyawa)\b",
    r"\b(tali).{0,40}(mengakhiri|akhiri semua|bunuh diri|mati|hidup|nyawa)\b",
    r"\b(tali).{0,5}(buat|untuk)?\s*(nanti malam|malam ini|besok pagi|sekarang|jadi)\b",
    r"\b(gantung|menjerat).{0,30}(diri|badan|leher|nyawa|hidup|saya|aku|gue)\b",

    # Referensi alat/metode lain — context-aware
    r"\b(gantung diri|gantung badan|gantung nyawa)\b",
    r"\b(minum obat).{0,20}(banyak|semua|overdosis|sekaligus|habis|mati|nyawa|hidup)\b",
    r"\b(obat).{0,20}(bunuh|mati|akhiri|hidup|nyawa|diri)\b",
    r"\b(lompat).{0,25}(gedung|jembatan|jendela|atap|lantai hidup|mati)\b",
    r"\b(iris|potong|sayat|luka).{0,15}(nadi|tangan|pergelangan|leher|nyawa|diri)\b",
    r"\b(siapin|siapkan|menyiapkan|udah siapin|kepengen).{0,20}(tali|obat|pisau|racun|cara)\b",
    r"\b(racun|zat).{0,15}(minum|telan|makan)\b",

    # Explicit intent + method combination
    r"\b(berpikir untuk).{0,30}(mengakhiri|akhiri|bunuh|mati|gantung|lompat|luka)\b",
    r"\b(ingin|pengen|mau|ingin sekali).{0,40}(mengakhiri|akhiri|bunuh|mati|pergi selamanya)\b",
    r"\b(mengakhiri semua ini|akhiri semua ini|akhiri hidup|akhiri saja)\b",
    r"\b(rasanya (aku|gue|saya) ingin mengakhiri|ingin (aku|gue|saya) (mati|bunuh diri))\b",

    # Metafora kematian — bervariasi
    r"\b(lebih baik (aku|gue|saya) (tidak ada|hilang|menghilang|pergi selamanya|tiada|mati))\b",
    r"\b(dunia|semua (akan|bakal|akan jadi) (lebih baik|lebih tenang|lebih senang) (tanpa aku|tanpa gue|tanpa saya|tanpa aku di dalamnya))\b",
    r"\b(tidak ingin (ada|hidup|bangun|lanjut) lagi)\b",
    r"\b(pengen (menghilang|hilang|pergi|mati) selamanya|selamanya gak ada lagi)\b",
    r"\b(ingin pergi).{0,30}(selamanya|untuk selamanya|dan tidak kembali|hilang untuk selamanya)\b",
    r"\b(tidak akan (ada|kembali|balik|bangun) lagi)\b",
    r"\b(mending (aku|gue|saya) (mati|hilang|gak ada))\b",
    r"\b(kasihan|sayang|rugi).{0,30}(masih (ada|hidup|coba)|sendiri)\b",  # Reversed self-pity ("kasihan orang lain karena aku masih ada")

    # Persiapan / rencana
    r"\b(sudah (merencanakan|menyiapkan|mempersiapkan|siap)).{0,30}(mati|akhir|pergi|bunuh|gantung)\b",
    r"\b(surat (untuk|buat|perpisahan|ucapan berakhir))\b",
    r"\b(leave note|pesan terakhir|pesan sebelum)\b",

    # Detailed planning/fixation
    r"\b(udah (pikir|rencanain|kepengen) gimana|udah (tau|tau jelas) caranya)\b",  # Already thought through method
    r"\b((cuma|tinggal) (tunggu|nunggu|tunggu waktu|nunggu momen)).{0,20}(yang tepat|tepet gitu)\b",
]

# ── L2 ────────────────────────────────────────────────────────────────────
KEYWORDS_L2 = [
    r"\b(sudah tidak tahan|udah gak tahan|gak sanggup lagi|udah ga kuat|nggak kuat lagi)\b",
    r"\b(tidak ada harapan|gak ada harapan|udah gak ada harapan|hopeless|putus asa)\b",
    r"\b(semua salahku|semua kesalahanku|ini salah aku semua|aku yang salah|gue yang salah)\b",
    r"\b(tidak ada yang peduli|gak ada yang peduli|ga ada yg peduli|tidak ada yang ngerti|gak ada yang ngerti)\b",
    r"\b(jadi beban|beban buat semua|cuma jadi beban|ngerasa jadi beban|rasa jadi beban|merasa jadi beban)\b",
    r"\b(rasanya ingin pergi (saja|aja)|ingin pergi saja)\b",
    r"\b(capek (hidup|sama hidup|dengan hidup|hidupnya)|capek hidup)\b",
    r"\b(bosan (hidup|sama hidup|hidupnya)|bosan hidup)\b",
    r"\b(hidup (gak ada artinya|tidak ada artinya|ga ada gunanya|tidak ada gunanya|gak berguna|tidak berguna))\b",
    r"\b(menyakiti diri|nyakitin diri|sakiti diri|cut myself|self harm|melukai diri)\b",
    r"\b(merasa (hampa|kosong|hampa saja|kosong saja))\b",
    r"\b(tidak bisa lagi|gak bisa lagi|udah tidak bisa|nggak sanggup)\b",
    r"\b(hanya ingin (istirahat|tidur|tidur lama|tidur selamanya))\b",
    r"\b(tidak ada (alasan|motivasi) untuk (terus|lanjut))\b",
]

# ── L1 ────────────────────────────────────────────────────────────────────
KEYWORDS_L1 = [
    r"\b(sangat lelah|kelelahan|udah capek banget|exhausted|cape sekali|kepenatan)\b",
    r"\b(tidak berharga|gak berharga|merasa gak berharga|ngerasa gak berharga|tidak berguna|tidak ada nilai)\b",
    r"\b(tidak berguna|gak berguna|merasa gak berguna|ngerasa ga berguna|tidak ada guna)\b",
    r"\b(menyesal lahir|nyesal hidup|nyesal pernah ada|nyesal dilahirkan|regret being born)\b",
    r"\b(dunia (lebih baik|akan lebih baik) tanpa aku|lebih baik tanpa aku)\b",
    r"\b(ingin menghilang|pengen menghilang|ingin lenyap|pengen lenyap|ingin hilang)\b",
    r"\b(rasanya ingin pergi|ngerasa ingin pergi|feeling wanna go)\b",
    r"\b(tidak ada motivasi|gak ada motivasi|udah gak punya motivasi)\b",
    r"\b(merasa sendirian|sendirian aja|sepi banget|kesepian)\b",
    r"\b(merasa ditinggalkan|merasa ditolak|merasa tidak diterima)\b",
]


def layer1_detect(text: str) -> tuple[str, float]:
    text_lower = text.lower()

    for pattern in KEYWORDS_L3_EKSPLISIT:
        if re.search(pattern, text_lower):
            return "L3", 0.95

    for pattern in KEYWORDS_L3_IMPLISIT:
        if re.search(pattern, text_lower):
            return "L3", 0.88

    for pattern in KEYWORDS_L2:
        if re.search(pattern, text_lower):
            return "L2", 0.80

    for pattern in KEYWORDS_L1:
        if re.search(pattern, text_lower):
            return "L1", 0.60

    return "NORMAL", 0.05


# ── Quick test ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    cases = [
        # ═══ L3 — EXPLICIT INTENT + METHOD ═════════════════════════════════
        ("Terkandang, saya berpikir untuk membeli tali dan mengakhiri semua ini", "L3"),
        ("Rasanya aku ingin mengakhiri semua ini",                                "L3"),
        ("Tali 2 meter yang aku beli kemarin terasa memanggilku",                 "L3"),
        ("Pengen gantung diri rasanya",                                           "L3"),
        ("Aku mau bunuh diri, udah gak kuat",                                    "L3"),
        ("Semua akan lebih baik tanpa aku",                                       "L3"),
        ("Aku udah siapin tali buat nanti malam",                                 "L3"),
        ("Udah beli obat banyak, mau diminum sekaligus",                         "L3"),
        ("Minding me pergi selamanya, udah gak ada gunanya",                      "L3"),
        ("Udah tau caranya, tinggal tunggu momen",                                "L3"),
        ("Udah rencanain semuanya dari A sampai Z",                               "L3"),

        # ═══ L2 — SERIOUS DISTRESS / HOPELESSNESS ═════════════════════════
        ("Rasanya ingin pergi saja",                                              "L2"),
        ("Capek hidup, gak ada harapan",                                          "L2"),
        ("Jadi beban buat semua orang, mending aku gak ada",                      "L2"),
        ("Hanya ingin tidur dan gak bangun lagi",                                 "L2"),
        ("Udah gak tahan lagi dengan semua ini",                                  "L2"),
        ("Tidak ada yang bisa aku lakukan, putus asa total",                      "L2"),

        # ═══ L1 — EARLY WARNING / HOPEFUL LANGUAGE ═════════════════════════
        ("Pengen menghilang dari semua ini",                                      "L1"),
        ("Merasa tidak ada nilai lagi, capek banget",                             "L1"),
        ("Sendirian aja kayaknya",                                                "L1"),
        ("Merasa ditolak oleh semua orang",                                       "L1"),

        # ═══ NORMAL — NO FALSE POSITIVE ════════════════════════════════════
        ("Hari ini seru banget makan sama teman",                                 "NORMAL"),
        ("Lagi banyak bercanda sama teman wkwkwk",                               "NORMAL"),
        ("Saya merasa sedih akhir-akhir ini tapi masih bisa handle",              "NORMAL"),
        ("Beli tali untuk jemuran kemarin",                                       "NORMAL"),  # Context: tali jemuran
        ("Lagi beli tali rafia di warung untuk kandang ayam",                     "NORMAL"),  # Explicit non-crisis context
        ("Beban kerja ga masuk akal, gaji sedikit",                               "NORMAL"),  # Complaint, not crisis thought
        ("Minum obat buat demam baru sembuh",                                     "NORMAL"),  # Therapeutic use
        ("Lompat-lompat seneng banget waktu main basket",                         "NORMAL"),  # Innocent context
    ]

    print("=" * 65)
    print("Layer 1 — Full Test")
    print("=" * 65)
    correct = 0
    for text, expected in cases:
        level, _ = layer1_detect(text)
        ok = level == expected
        correct += int(ok)
        print(f"{'PASS' if ok else 'FAIL'} [{level:6s}] {text[:60]}")
        if not ok:
            print(f"         Expected: {expected}")
    print(f"\nHasil: {correct}/{len(cases)} benar")