# Karuna AI — Product Requirements Document (PRD)

**Version:** 1.0
**Status:** Draft
**Last Updated:** March 2026
**Team:** BaldManAndTwoIdiots (Mukti Jaenal, Solo Manurung, Bintang Aryanto)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Goals &amp; Success Metrics](#3-goals--success-metrics)
4. [User Personas](#4-user-personas)
5. [Platform Architecture Overview](#5-platform-architecture-overview)
6. [AI System Design](#6-ai-system-design)
7. [Feature Requirements](#7-feature-requirements)
8. [Psychologist Grade System](#8-psychologist-grade-system)
9. [AI Service Level System](#9-ai-service-level-system)
10. [Subscription &amp; Monetization](#10-subscription--monetization)
11. [Data Privacy &amp; Security](#11-data-privacy--security)
12. [Non-Functional Requirements](#12-non-functional-requirements)
13. [UI/UX Requirements](#13-uiux-requirements)
14. [External Integrations](#14-external-integrations)
15. [Out of Scope (v1.0)](#15-out-of-scope-v10)
16. [Risks &amp; Mitigations](#16-risks--mitigations)
17. [Glossary](#17-glossary)

---

## 1. Executive Summary

### What is Karuna AI?

Karuna AI adalah platform kesehatan mental berbasis AI yang berfungsi sebagai **jembatan** antara individu yang membutuhkan dukungan emosional dan psikolog profesional berlisensi. Platform ini bukan aplikasi terapi mandiri — melainkan infrastruktur yang meningkatkan aksesibilitas dan efektivitas layanan psikologi yang sudah ada.

Model bisnis platform ini adalah **B2C2B (Business-to-Consumer-to-Business)**: pengguna individu membayar subscription untuk mengakses AI companion dan psikolog, sementara psikolog membayar platform subscription untuk bergabung sebagai profesional terverifikasi dalam marketplace.

### Core Value Proposition

| Untuk Siapa        | Nilai yang Diterima                                                                                    |
| ------------------ | ------------------------------------------------------------------------------------------------------ |
| **End User** | Ekspresi emosi bebas tanpa stigma → AI merangkum → Psikolog memahami lebih cepat, sesi lebih efektif |
| **Psikolog** | Konteks klien sudah tersedia sebelum sesi → hemat 30–40 menit warm-up → penanganan lebih tepat      |
| **Sistem**   | Crisis detection memastikan tidak ada pengguna yang jatuh melalui celah tanpa terdeteksi               |

### Tagline

> *"Technology that listens, humans that heal."*

---

## 2. Problem Statement

### 2.1 Mental Health Access Gap di Asia Tenggara

Data menunjukkan krisis akses layanan kesehatan mental yang signifikan di seluruh ASEAN:

| Negara              | Statistik Kunci                                                                                                     |
| ------------------- | ------------------------------------------------------------------------------------------------------------------- |
| **Indonesia** | 9.8% dewasa mengalami gangguan emosional (Riskesdas 2018); <5% mencari bantuan; 0.39 psikiater per 100.000 penduduk |
| **Filipina**  | 3.6 juta+ dewasa dengan gangguan mental; hanya 2–3% menerima penanganan (DOH, 2021)                                |
| **Thailand**  | 12.3% dewasa menunjukkan gejala; 1 psikiater per 20.000 penduduk (DMH, 2021)                                        |
| **Malaysia**  | 29.2% dewasa 16+ menunjukkan gejala depresi (NHMS 2019); disparitas urban-rural parah                               |
| **Vietnam**   | WHO estimasi prevalensi 14.9%; <1% anggaran kesehatan untuk mental health                                           |
| **ASEAN**     | Estimasi USD 26 miliar/tahun hilang produktivitas dari kondisi tidak tertangani (WEF, 2022)                         |

### 2.2 Tiga Hambatan Struktural

**Hambatan 1 — Stigma Sosial**
Di sebagian besar budaya ASEAN, mengunjungi psikolog masih diidentikkan dengan penyakit mental berat. Persepsi ini menekan upaya mencari bantuan sejak dini dan mendorong penyembunyian distress — terutama pada pria dan individu di komunitas konservatif. Karuna AI menyediakan ruang ekspresi anonim dan bebas stigma sebagai titik masuk pertama.

**Hambatan 2 — Biaya Finansial**
Satu sesi klinis di Indonesia berkisar IDR 300.000–700.000 (USD 19–45) tanpa jaminan kecocokan. Ini merepresentasikan 10–23% penghasilan bulanan median pekerja urban. Dengan model tiered subscription mulai dari IDR 79.000/bulan, Karuna AI menurunkan barrier finansial secara signifikan.

**Hambatan 3 — Gesekan Struktural di Titik Masuk**
Banyak individu yang bersedia mencari bantuan tidak tahu harus mulai dari mana, tidak memiliki kosakata untuk mendeskripsikan kondisi mereka kepada orang asing, dan mendapati sesi pertama tidak produktif karena 30–40 menit dihabiskan untuk context-gathering dasar. AI summary yang dihasilkan Karuna AI mengeliminasi hambatan ini sepenuhnya.

### 2.3 Perspektif Psikolog

Dari sisi penawaran, psikolog berlisensi menghadapi tantangan struktural sendiri:

- Tidak ada mekanisme intake terstruktur sebelum sesi pertama
- Tidak ada pemantauan antar-sesi untuk klien berisiko
- Platform booking yang ada hanya menawarkan penjadwalan, tanpa clinical insight
- Pipeline klien yang terbatas dan tidak konsisten

---

## 3. Goals & Success Metrics

### 3.1 Product Goals

| Goal                               | Deskripsi                                                                                      |
| ---------------------------------- | ---------------------------------------------------------------------------------------------- |
| **G1 — Aksesibilitas**      | Menyediakan titik masuk layanan mental health yang bebas stigma, tersedia 24/7, dan terjangkau |
| **G2 — Efektivitas Klinis** | Mengurangi waktu warm-up sesi psikolog sebesar 30–40 menit melalui AI summary terstruktur     |
| **G3 — Keamanan Krisis**    | Tidak ada pengguna dalam kondisi krisis yang tidak terdeteksi atau tidak ditangani             |
| **G4 — Privasi**            | Zero-access architecture: tidak ada konten sesi yang bisa dibaca oleh admin platform           |
| **G5 — Skalabilitas**       | Arsitektur yang mendukung ekspansi ke seluruh ASEAN pada Year 2                                |

### 3.2 Success Metrics (Year 1 — Indonesia)

| Metrik                          | Target                                           |
| ------------------------------- | ------------------------------------------------ |
| Registered users                | 25.000                                           |
| Active verified psychologists   | 200                                              |
| Monthly active users (MAU)      | 10.000                                           |
| Paid subscriber conversion rate | ≥ 15% dari registered users                     |
| Session warm-up time reduction  | 30–40 menit per sesi                            |
| L3 crisis response time         | < 5 menit dari deteksi hingga psikolog merespons |
| CDS false-negative rate         | < 5%                                             |
| App store rating                | ≥ 4.5/5                                         |
| Psychologist satisfaction score | ≥ 4.0/5                                         |

---

## 4. User Personas

### Persona 1 — End User: "Dinda, 23 tahun, Mahasiswi Tingkat Akhir"

**Latar Belakang:** Mahasiswi semester akhir di Jakarta, menghadapi tekanan skripsi, konflik keluarga, dan kecemasan akan masa depan. Aktif di media sosial, menggunakan Spotify dan Netflix dengan langganan.

**Pain Points:**

- Merasa tidak ada yang bisa diajak bicara jujur tanpa menghakimi
- Takut dianggap "lebay" jika curhat ke teman
- Tidak mampu bayar sesi psikolog reguler (IDR 400.000+/sesi)
- Tidak tahu cara memulai atau apa yang harus dikatakan ke psikolog

**Goals di Platform:**

- Punya ruang aman untuk mengekspresikan perasaan kapan saja
- Mendapat pemahaman tentang kondisi emosionalnya
- Jika perlu, terhubung ke psikolog yang sudah "mengenal" kondisinya

**Subscription Likely:** Free/Basic (Level 1–2)

---

### Persona 2 — Psikolog: "Dr. Reza, 38 tahun, Psikolog Klinis Berpengalaman"

**Latar Belakang:** Psikolog berlisensi HIMPSI dengan 10 tahun pengalaman, praktek di Jakarta Selatan dan melayani klien online. Kewalahan dengan jadwal, menghabiskan banyak waktu untuk intake dasar di setiap sesi pertama.

**Pain Points:**

- Setiap klien baru membutuhkan 30–40 menit hanya untuk menjelaskan kondisi dasar
- Tidak ada visibilitas kondisi klien di antara sesi
- Klien sering datang saat kondisi sudah sangat parah karena menunda-nunda
- Pipeline klien tidak stabil dan tidak bisa diprediksi

**Goals di Platform:**

- Menerima konteks klien yang terstruktur sebelum sesi pertama
- Monitoring kondisi emosional klien antar-sesi
- Mendapatkan pipeline klien yang lebih konsisten dan berkualitas

**Role di Platform:** Grade A — Senior Specialist

---

### Persona 3 — Pengguna Krisis: "Aldi, 19 tahun, Mahasiswa Baru"

**Latar Belakang:** Mahasiswa baru di kota asing, pertama kali jauh dari keluarga, mengalami isolasi sosial dan tekanan akademik berat. Tidak punya jaringan dukungan lokal.

**Pain Points:**

- Tidak ada orang yang bisa dihubungi saat kondisi memburuk di malam hari
- Tidak tahu nomor atau cara mengakses layanan krisis
- Merasa tidak ada yang peduli dengan kondisinya

**Critical Need:** Crisis detection yang bekerja bahkan saat dia tidak secara eksplisit meminta bantuan, dan eskalasi ke profesional manusia yang nyata.

---

### Persona 4 — Kontak Darurat: "Ibu Dinda, 50 tahun"

**Latar Belakang:** Orang tua yang tidak menyadari kondisi anaknya memburuk hingga terlambat.

**Need di Platform:** Notifikasi otomatis (SMS/WA) saat sistem mendeteksi kondisi krisis pada anaknya, tanpa harus memiliki akun platform.

---

## 5. Platform Architecture Overview

### 5.1 Tiga Komponen Utama

```
┌─────────────────────────────────────────────────────────────┐
│                        KARUNA AI                            │
├─────────────────┬───────────────────┬───────────────────────┤
│   USER APP      │  PROFESSIONAL     │   AI & BACKEND        │
│   (Android/iOS) │  DASHBOARD (Web)  │   ENGINE              │
│                 │                   │                       │
│ • Curhat AI     │ • Inbox Summary   │ • NLP Emotion         │
│ • Summary       │ • EDA Visualizer  │ • Crisis Detection    │
│ • Psikolog      │ • Crisis Alert    │ • Summary Generator   │
│ • Subscription  │ • Jadwal & Klien  │ • LLM Orchestration   │
└─────────────────┴───────────────────┴───────────────────────┘
```

### 5.2 Alur Inti Platform

```
User curhat dengan AI
        ↓
AI menganalisis emosi + CDS real-time per pesan
        ↓
Sesi berakhir → AI generate Summary terstruktur
        ↓
User melihat preview Summary
        ↓ (dengan explicit consent)
User memilih Psikolog berdasarkan grade & spesialisasi
        ↓
Psikolog menerima Summary di Dashboard
        ↓
Psikolog merespons: rekomendasikan sesi / tidak
        ↓
User & Psikolog melakukan sesi konsultasi
```

**Jika di titik mana pun CDS mendeteksi L2/L3:**

```
CDS trigger → Crisis Screen di User App
           → Push alert ke Psikolog terhubung
           → Notifikasi ke Kontak Darurat
           → Eskalasi ke On-Call Pro jika tidak ada respons
```

---

## 6. AI System Design

Karuna AI dibangun di atas empat subsistem AI yang terintegrasi:

### S1 — Conversational LLM (AI Companion)

**Fungsi:** Merespons curhat user dengan empati, tanpa diagnosis, tanpa solusi medis. Kualitas dan kapabilitas AI ini meningkat sesuai subscription tier.

**Teknologi:** GPT-4o (Levels 1–3), GPT-5 tier (Level 4 Premium). Google Gemini 1.5 Pro sebagai fallback.

**Aturan Output yang Tidak Boleh Dilanggar:**

- AI tidak boleh memberikan atau menyiratkan diagnosis medis apapun
- AI tidak boleh memberikan saran medis atau rekomendasi obat
- AI tidak boleh bersikap dismissive atau toxic positivity
- Semua output melewati clinical output validator sebelum dikirim ke user
- Tone: supportive, non-judgmental, pacing lambat saat kondisi distress terdeteksi

**Kapabilitas per Tier:**

- Level 0–1: Journaling empatik dasar, context window terbatas
- Level 2: Context awareness yang lebih baik, emotion timeline
- Level 3: Multi-turn memory, voice journaling, full EDA
- Level 4: Model tier tertinggi, historical session analysis, on-call pro access

---

### S2 — NLP Emotion Engine

**Fungsi:** Menganalisis setiap pesan user secara real-time untuk mendeteksi emosi dominan, intensitas, topik, dan cognitive distortion patterns.

**Teknologi:** Fine-tuned IndoBERT (multi-task classifier) pada dataset EmoSet-ID + IndoNLU + internal labeled dataset (~500 sampel dari psikolog).

**Output per Pesan:**

```json
{
  "dominant_emotion": "sadness",
  "intensity": 0.72,
  "secondary_emotion": "anxiety",
  "topics": ["academic_pressure", "family_conflict"],
  "cognitive_flags": ["catastrophizing", "mind_reading"],
  "cds_input_score": 0.15
}
```

**Target Akurasi:** > 80% untuk klasifikasi 7 emosi dasar.

**Catatan Penting:** Output S2 adalah decision-support tool. Tidak pernah ditampilkan sebagai diagnosis kepada user. Selalu disertai disclaimer "Estimasi AI, bukan diagnosis klinis."

---

### S3 — Crisis Detection System (CDS)

**Ini adalah subsistem paling kritis. Uptime minimum 99.9%.**

**Fungsi:** Mendeteksi risiko bunuh diri dan self-harm secara real-time di setiap pesan, mengklasifikasikan ke dalam 3 level risiko, dan men-trigger protokol eskalasi yang sesuai.

**Teknologi:** Keyword matching + contextual BERT + conversation history scoring + Columbia C-SSRS framework (diterjemahkan dan diadaptasi).

**Tiga Level CDS:**

| Level        | Nama     | Trigger                                                                | Respons AI                                                                           | Respons Sistem                                                                                                                           |
| ------------ | -------- | ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------- |
| **L1** | Distress | Keputusasaan, isolasi sosial, kelelahan emosional (NLP context-aware)  | AI beralih ke tone lebih lambat dan validating; tawarkan opsi bicara dengan psikolog | Tidak ada eskalasi otomatis; transparan ke user                                                                                          |
| **L2** | At-Risk  | Referensi ambigu tentang menghilang/kematian; pola keputusasaan subtil | AI melanjutkan percakapan secara natural                                             | Silent push notification ke psikolog terhubung dengan kalimat trigger ter-highlight; psikolog memutuskan respons                         |
| **L3** | Crisis   | Intent eksplisit, metode, timeline, atau rencana self-harm             | AI pause mode percakapan; tampilkan Crisis Screen                                    | Push alert ke psikolog <30 detik; SMS/WA ke kontak darurat; eskalasi ke On-Call Pro dalam 5 menit; hard fallback 119 ext.8 di T+15 menit |

**Protokol Eskalasi L3 (Timeline Detail):**

```
T+00:00 → CDS deteksi L3; AI pause; Crisis Screen tampil di user
T+00:10 → Pesan stabilisasi pre-approved ditampilkan
T+00:15 → Push notif + badge merah ke Psikolog terhubung
T+00:20 → Hotline krisis (119 ext 8) tampil di layar user
T+00:30 → SMS/WA ke kontak darurat user
T+05:00 → Jika Psikolog belum respons → eskalasi ke On-Call Pro (rotasi)
T+10:00 → Jika On-Call belum respons → notif admin Karuna AI
T+15:00 → Hard fallback: instruksi langsung hubungi 119 ext 8 atau IGD terdekat
T+24:00 → Follow-up check-in otomatis ke user
Post    → Audit log tersimpan permanen; semua event immutable
```

**Prinsip Desain Crisis Screen:**

- Warna: Deep navy, bukan merah (untuk mencegah panic response)
- Bahasa: Hangat, tidak alarming, tidak menghakimi
- Konten: Dikembangkan bersama psikolog klinis berlisensi
- Tidak boleh ada tombol "Dismiss" atau "Tutup" sampai kontak psikolog terkonfirmasi

---

### S4 — AI Summary Generator

**Fungsi:** Mengagregasi seluruh data sesi — emotion timeline, topik, cognitive distortions, CDS flags — menjadi dokumen klinis terstruktur yang dapat langsung digunakan oleh psikolog.

**Trigger:** Hanya dijalankan jika user secara eksplisit memilih "Buat Summary" di akhir sesi. Tidak otomatis.

**Format Output Summary (JSON Schema):**

```json
{
  "session_id": "uuid",
  "generated_at": "timestamp",
  "main_themes": ["academic pressure", "fear of failure", "family dynamics"],
  "emotion_timeline": [
    {"timestamp": "T+2min", "dominant": "anxiety", "intensity": 0.6},
    {"timestamp": "T+8min", "dominant": "sadness", "intensity": 0.85}
  ],
  "dominant_emotions": ["sadness", "anxiety"],
  "cognitive_distortions": ["catastrophizing", "all-or-nothing thinking"],
  "risk_flags": {
    "cds_max_level": 1,
    "trigger_sentences": ["rasanya tidak ada gunanya lagi mencoba"]
  },
  "psychologist_note": "User menunjukkan pola pikir katastrofik yang konsisten terkait performa akademik. Perlu eksplorasi lebih lanjut terkait ekspektasi keluarga.",
  "recommended_focus": ["cognitive restructuring", "stress management"]
}
```

**Alur Consent Summary:**

1. User selesai sesi → pilih "Buat Summary"
2. User melihat preview summary lengkap
3. User bisa mengedit/meredact informasi pribadi (nama, lokasi, dll)
4. User memilih: Kirim ke Psikolog / Simpan Privat / Hapus Permanen
5. Jika kirim → user memilih psikolog dari marketplace
6. Summary dikirim terenkripsi ke dashboard psikolog yang dipilih
7. **Jika tidak consent → tidak ada data yang diteruskan ke siapapun**

---

### EDA Engine (Emotion Detection Analysis)

**Fungsi:** Subsistem AI terpisah yang menganalisis emosi dari tiga modalitas secara paralel selama sesi konsultasi aktif dengan psikolog.

| Modalitas                | Input                                      | Teknologi                          | Output                            | Target Akurasi |
| ------------------------ | ------------------------------------------ | ---------------------------------- | --------------------------------- | -------------- |
| **Teks (NLP)**     | Pesan curhat                               | Fine-tuned IndoBERT                | 7 emosi + intensitas (0–1)       | > 80%          |
| **Suara**          | Audio sesi (dengan izin)                   | Acoustic feature extraction + LSTM | Arousal, Valence, Dominance (VAD) | > 70%          |
| **Ekspresi Wajah** | Video frame kamera (dengan izin eksplisit) | FER berbasis MobileNetV3           | 6 ekspresi Ekman                  | > 65%          |

**Aturan EDA:**

- Setiap modalitas memerlukan consent eksplisit terpisah di onboarding
- User dapat mencabut izin modalitas kapan saja tanpa kehilangan akses layanan
- Data wajah tidak boleh disimpan lebih dari durasi sesi (diproses real-time, langsung di-discard)
- Hasil EDA ditampilkan di dashboard psikolog sebagai visualisasi grafis, bukan angka mentah
- Selalu disertai disclaimer: "Ini adalah estimasi AI, bukan diagnosis klinis"
- Latensi total pemrosesan ketiga modalitas: < 3 detik

---

## 7. Feature Requirements

### 7.1 Modul Autentikasi & Onboarding

| ID         | Requirement                                                                                         | Prioritas |
| ---------- | --------------------------------------------------------------------------------------------------- | --------- |
| FR-AUTH-01 | Registrasi via email dan Google OAuth                                                               | Critical  |
| FR-AUTH-02 | Verifikasi email sebelum akun aktif                                                                 | Critical  |
| FR-AUTH-03 | Onboarding wajib: nama, usia, min. 1 kontak darurat, persetujuan protokol krisis                    | Critical  |
| FR-AUTH-04 | Psikolog wajib upload STR, foto diri, jadwal ketersediaan saat registrasi; review admin maks 48 jam | Critical  |
| FR-AUTH-05 | Autentikasi biometrik (fingerprint/Face ID) untuk login ulang                                       | High      |
| FR-AUTH-06 | Reset password via email + 2FA support                                                              | High      |

**Catatan Onboarding:**

- Tidak bisa di-skip. User harus menyelesaikan onboarding sebelum akses fitur utama
- Consent EDA per modalitas ditanyakan di onboarding (bukan satu consent untuk semua)
- User di bawah 18 tahun memerlukan persetujuan orang tua (verified)
- Usia minimum: 17 tahun

---

### 7.2 Modul Sesi Curhat (AI Journaling)

| ID         | Requirement                                                                                                         | Prioritas |
| ---------- | ------------------------------------------------------------------------------------------------------------------- | --------- |
| FR-CHAT-01 | User dapat memulai sesi kapan saja; AI merespons dalam Bahasa Indonesia atau Inggris                                | Critical  |
| FR-CHAT-02 | AI merespons dengan empati; tidak memberi diagnosis, tidak memberi solusi medis; tone supportive dan non-judgmental | Critical  |
| FR-CHAT-03 | AI mencatat seluruh percakapan dan menghasilkan summary terstruktur di akhir sesi                                   | Critical  |
| FR-CHAT-04 | User dapat menutup sesi tanpa membuat summary; data tidak disimpan jika user memilih ini                            | High      |
| FR-CHAT-05 | AI mendukung input teks, voice-to-text, dan gambar (foto ekspresi, drawing); gambar dianalisis EDA                  | High      |
| FR-CHAT-06 | Sesi dapat dilanjutkan (resume) dalam 24 jam jika terputus                                                          | High      |
| FR-CHAT-07 | AI mendeteksi bahasa campuran code-switching Indonesia–Inggris                                                     | Medium    |
| FR-CHAT-08 | User dapat melihat riwayat sesi curhat maksimal 90 hari ke belakang                                                 | Medium    |
| FR-CHAT-09 | AI tidak menyimpan konten sesi jika user tidak setuju di onboarding (GDPR/UU PDP)                                   | Critical  |
| FR-CHAT-10 | Tombol "Aku baik-baik saja" untuk menutup sesi cepat tanpa analisis                                                 | Medium    |

---

### 7.3 Modul Summary & Pengiriman ke Psikolog

| ID        | Requirement                                                                                                    | Prioritas |
| --------- | -------------------------------------------------------------------------------------------------------------- | --------- |
| FR-SUM-01 | Summary berisi: tema utama, emosi terdeteksi, intensitas, pola pikir, dan flag risiko                          | Critical  |
| FR-SUM-02 | User melihat preview summary sebelum memutuskan apakah dikirim ke psikolog; user bisa edit nama/detail pribadi | Critical  |
| FR-SUM-03 | Jika user setuju kirim, sistem menampilkan daftar psikolog tersedia beserta grade, spesialisasi, dan rating    | Critical  |
| FR-SUM-04 | Psikolog menerima push notification saat summary baru masuk; SLA baca: 24 jam (non-krisis)                     | Critical  |
| FR-SUM-05 | User menerima notifikasi saat psikolog telah membaca summary                                                   | High      |
| FR-SUM-06 | Psikolog memberikan respons awal: rekomendasi (perlu sesi / tidak) + pesan singkat (maks 200 kata)             | Critical  |

---

### 7.4 Modul Konsultasi (Chat / Voice / Video)

| ID        | Requirement                                                                                                       | Prioritas |
| --------- | ----------------------------------------------------------------------------------------------------------------- | --------- |
| FR-CON-01 | User memilih mode konsultasi: in-app chat, voice call, atau video call                                            | Critical  |
| FR-CON-02 | Penjadwalan sesi dengan kalender ketersediaan psikolog; zona waktu terdeteksi otomatis                            | Critical  |
| FR-CON-03 | Sesi video/voice menggunakan enkripsi end-to-end (WebRTC + DTLS-SRTP)                                             | Critical  |
| FR-CON-04 | EDA engine menganalisis emosi user secara real-time selama sesi (dengan izin); hasil tampil di dashboard psikolog | High      |
| FR-CON-05 | Psikolog dapat membuat catatan sesi yang tidak terlihat oleh user                                                 | High      |
| FR-CON-06 | Penjadwalan ulang dengan notifikasi min. 2 jam sebelum sesi                                                       | High      |
| FR-CON-07 | Rekaman sesi (jika diaktifkan) hanya boleh diakses psikolog dan user — zero-access untuk admin                   | Critical  |
| FR-CON-08 | Setelah sesi selesai, user memberikan rating dan feedback anonim ke psikolog                                      | Medium    |

---

### 7.5 Modul Subscription & Pembayaran

| ID        | Requirement                                                                              | Prioritas |
| --------- | ---------------------------------------------------------------------------------------- | --------- |
| FR-PAY-01 | Subscription bulanan dengan tier: Free Trial, Free Registered, Basic, Plus, Premium      | Critical  |
| FR-PAY-02 | Integrasi Midtrans (Indonesia) dan Stripe (regional ASEAN)                               | Critical  |
| FR-PAY-03 | Auto-renewal dengan notifikasi 3 hari sebelum renewal                                    | High      |
| FR-PAY-04 | User dapat downgrade atau cancel kapan saja; refund prorata untuk Premium tier           | High      |
| FR-PAY-05 | Revenue share psikolog: 70% dari tarif sesi; payout otomatis ke rekening terdaftar       | Critical  |
| FR-PAY-06 | Psikolog membayar platform subscription IDR 299.000/bulan untuk bergabung di marketplace | High      |

---

### 7.6 Modul Psikolog (Professional Dashboard)

| ID        | Requirement                                                                        | Prioritas |
| --------- | ---------------------------------------------------------------------------------- | --------- |
| FR-PRO-01 | Psikolog menerima inbox summary dengan badge unread, filter urgensi, preview cepat | Critical  |
| FR-PRO-02 | Detail view summary: emosi terdeteksi, kalimat ter-highlight, riwayat user         | Critical  |
| FR-PRO-03 | EDA Visualizer: grafik emosi real-time saat sesi konsultasi berlangsung            | High      |
| FR-PRO-04 | Crisis Alert: notifikasi L2/L3 dengan detail pemicu dan tombol "Respond Now"       | Critical  |
| FR-PRO-05 | Manajemen jadwal: kalender, set jam buka, block waktu                              | Critical  |
| FR-PRO-06 | Daftar klien aktif: riwayat interaksi, catatan pribadi, progress emosi             | High      |
| FR-PRO-07 | Laporan keuangan: pendapatan bulan ini, invoice, penarikan dana                    | High      |
| FR-PRO-08 | Psikolog hanya menerima klien sesuai grade-tier match subscription                 | Critical  |

---

### 7.7 Modul Crisis Detection (CDS)

| ID        | Requirement                                                                               | Prioritas |
| --------- | ----------------------------------------------------------------------------------------- | --------- |
| FR-CDS-01 | CDS berjalan di semua sesi, semua tier, tanpa pengecualian                                | Critical  |
| FR-CDS-02 | Deteksi L1: tone AI berubah lebih slow-paced dan validating secara otomatis               | Critical  |
| FR-CDS-03 | Deteksi L2: silent push notif ke psikolog terhubung dengan kalimat trigger                | Critical  |
| FR-CDS-04 | Deteksi L3: Crisis Screen tampil, eskalasi penuh sesuai timeline T+00:00 s/d T+24:00      | Critical  |
| FR-CDS-05 | Semua event CDS tersimpan dalam immutable audit log                                       | Critical  |
| FR-CDS-06 | False-negative rate target < 5% untuk L3                                                  | Critical  |
| FR-CDS-07 | Setiap perubahan kode CDS wajib sign-off psikolog klinis senior sebelum production deploy | Critical  |

---

## 8. Psychologist Grade System

Karuna AI mengimplementasikan sistem grading psikolog yang transparan dan multi-dimensional. Grade menentukan psikolog mana yang dapat diakses oleh subscription tier tertentu.

### Kriteria Grading

| Grade             | Nama                     | Kriteria                                                                                                                                                         |
| ----------------- | ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Grade A** | Senior Specialist        | S2/S3 Psikologi Klinis; STR aktif; 10+ tahun praktik; 1.000+ kasus terdokumentasi; pengalaman kasus kompleks (trauma, mood disorders berat, crisis intervention) |
| **Grade B** | Experienced Practitioner | S1/S2 Psikologi; STR aktif; 5–10 tahun praktik; 300–999 kasus; kasus kompleks sedang; rating platform min. 4.5/5 dengan 50+ ulasan                             |
| **Grade C** | Qualified Practitioner   | S1 Klinis/Psikologi; STR aktif; 1–5 tahun praktik; 50–299 kasus; generalist support; rating min. 4.0/5 dengan 20+ ulasan                                       |
| **Grade D** | Associate (Supervised)   | S1 Psikologi (lulusan baru); STR aktif; <1 tahun praktik independen; wajib supervisi untuk kasus kompleks; cocok untuk distress ringan dan psikoedukasi          |

### Proses Grading

- **Onboarding:** Psikolog baru di-assess dan ditempatkan pada grade saat pertama bergabung
- **Semi-annual review:** Grade dievaluasi ulang setiap 6 bulan berdasarkan metrik platform (rating, volume kasus, peer review)
- **Dynamic update:** Grade dapat naik atau turun berdasarkan performa aktual di platform
- **Transparansi:** Grade ditampilkan secara publik di profil psikolog

### Subscription-Grade Access Matrix

| Tier Subscription     | Grade Psikolog yang Dapat Diakses                             |
| --------------------- | ------------------------------------------------------------- |
| Free Trial            | Summary only (tidak ada pencocokan psikolog)                  |
| Free Registered       | Grade D (Associate, supervised)                               |
| Basic (IDR 79K/mo)    | Grade C–D                                                    |
| Plus (IDR 149K/mo)    | Grade B–C (user dapat memilih grade)                         |
| Premium (IDR 249K/mo) | Grade A–B (user memilih grade preferensi; akses On-Call Pro) |

### Matching Algorithm

Psikolog di dalam setiap grade tier dirandominasi untuk mencegah bias sistematis dan memastikan distribusi klien yang adil. Filter tambahan yang dapat dipilih user: spesialisasi, preferensi bahasa, ketersediaan waktu, dan rating.

---

## 9. AI Service Level System

AI companion itu sendiri adalah produk bertingkat — bukan fitur flat. Ini menciptakan insentif subscription yang bermakna sekaligus memastikan semua user memiliki akses ke AI yang aman secara klinis, terlepas dari tier.

| AI Level                      | Subscription            | Kapabilitas AI                                                                                 |
| ----------------------------- | ----------------------- | ---------------------------------------------------------------------------------------------- |
| **Level 0 — Trial**    | Free (tanpa registrasi) | 10 respons AI; journaling empatik dasar; CDS selalu aktif                                      |
| **Level 1 — Standard** | Free (registered)       | Maks 10 respons/sesi, 3 sesi/bulan; NLP emotion analysis standar                               |
| **Level 2 — Enhanced** | Basic (IDR 79K/mo)      | Unlimited sesi; context awareness yang ditingkatkan; emotion timeline; 3 summary/bulan         |
| **Level 3 — Pro**      | Plus (IDR 149K/mo)      | Unlimited; advanced multi-turn memory; voice journaling; full EDA; priority matching           |
| **Level 4 — Premium**  | Premium (IDR 249K/mo)   | Semua Level 3 + model LLM tertinggi (setara GPT-5 tier); analisis historis; on-call pro access |

**Prinsip Level 0 (Trial):** User yang tidak terdaftar mendapatkan 10 respons AI gratis untuk merasakan value proposition sebelum komitmen registrasi atau subscription. Ini menurunkan barrier masuk pertama.

**CDS tidak pernah di-gate oleh tier.** Crisis detection aktif di semua level, termasuk Level 0 trial.

---

## 10. Subscription & Monetization

### 10.1 Model Revenue Dual

**Revenue Stream 1 — User Subscriptions:**

| Tier            | Harga                                 | Target Segmen                                              |
| --------------- | ------------------------------------- | ---------------------------------------------------------- |
| Free Trial      | Gratis (10 respons, tanpa registrasi) | Calon user baru                                            |
| Free Registered | Gratis (3 sesi/bulan)                 | User awal, budget terbatas                                 |
| Basic           | IDR 79.000/bulan                      | Mahasiswa, young professional                              |
| Plus            | IDR 149.000/bulan                     | Working professional dengan kebutuhan regular              |
| Premium         | IDR 249.000/bulan                     | User dengan kebutuhan klinis serius; akses psikolog senior |

**Revenue Stream 2 — Professional (Psikolog):**

| Item                           | Harga                                  |
| ------------------------------ | -------------------------------------- |
| Platform subscription psikolog | IDR 299.000/bulan                      |
| Revenue share sesi konsultasi  | 70% untuk psikolog, 30% untuk platform |
| On-call duty compensation      | IDR 150.000/jam                        |

**Proyeksi Year 1:** 10.000 paid users + 100 psikolog aktif ≈ IDR 1,28 miliar/bulan (~USD 80.000), target self-sufficient dalam Year 1.

---

## 11. Data Privacy & Security

Data privacy adalah komponen kepercayaan paling kritis dari platform mental health. Karuna AI memperlakukan keamanan data bukan sebagai checklist compliance, melainkan sebagai komitmen arsitektur inti.

### 11.1 Technical Security Guarantees

**End-to-End Encryption (E2E):**
Semua konten sesi — pesan journaling, input suara, summary — dienkripsi di perangkat user sebelum transmisi. Server backend hanya memproses ciphertext terenkripsi. Admin platform tidak dapat membaca konten sesi dalam kondisi apapun.

**Standar Enkripsi:**

- Data at-rest: AES-256 untuk semua data user di database
- Data in-transit: TLS 1.3 minimum untuk semua API calls
- Sesi voice/video: WebRTC + DTLS-SRTP

**Zero-Access Architecture:**
Bahkan jika terjadi server breach, konten sesi tidak dapat didekripsi tanpa private key user, yang tidak pernah disimpan di server.

**Anonymized Professional Summaries:**
Summary yang dikirim ke psikolog menggunakan alias pilihan user, bukan nama asli, kecuali user secara eksplisit consent untuk disclosure nama.

**Immutable Audit Log:**
Semua event akses data sensitif dicatat dalam audit trail tamper-proof yang disimpan selama 2 tahun. Ini memungkinkan akuntabilitas forensik penuh.

### 11.2 User Data Control Rights

| Hak                                    | Detail                                                                                                                            |
| -------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| **Selective Storage**            | User dapat memilih agar data sesi hanya tersimpan di AI processing layer dan dihapus dari persistent database segera setelah sesi |
| **Right to Be Forgotten (RTBF)** | User dapat request penghapusan semua data dalam 30 hari (UU PDP 2024, PDPA Thailand, PDPA Singapore)                              |
| **Granular EDA Consent**         | Setiap modalitas emotion detection (teks, suara, wajah) memerlukan consent terpisah yang dapat dicabut kapan saja                 |
| **Data Portability**             | User dapat mengekspor seluruh riwayat data dalam format machine-readable kapan saja                                               |

### 11.3 Legal Framework

**Data Processing Agreement (DPA):**
Semua psikolog di platform menandatangani DPA yang legally binding sebelum aktivasi, menetapkan kewajiban ketat tentang cara mereka menangani informasi klien.

**Professional Non-Disclosure Agreement (NDA):**
Psikolog menandatangani NDA yang secara khusus mencakup digital clinical summaries dan semua interaksi yang dimediasi platform.

**Platform Terms of Service:**
Secara eksplisit melarang penggunaan komersial, re-identifikasi, atau secondary sharing data user oleh psikolog.

**Breach Notification Protocol:**
Dalam hal insiden keamanan data, semua user yang terdampak akan dinotifikasi dalam 72 jam — melampaui standar GDPR dan selaras dengan persyaratan UU PDP.

### 11.4 Jaminan Keamanan Data kepada User

> 1. Konten sesi Anda terenkripsi end-to-end. Staff Karuna AI tidak dapat membacanya.
> 2. Anda memilih apa yang dibagikan dan kepada siapa. Tidak ada yang dikirim ke psikolog tanpa persetujuan aktif Anda.
> 3. Anda dapat menghapus semua data Anda kapan saja. Penghapusan bersifat lengkap, terverifikasi, dan dikonfirmasi kepada Anda.
> 4. Semua psikolog telah menandatangani perjanjian legal yang melindungi informasi Anda.
> 5. Jika pernah terjadi breach, Anda akan dinotifikasi dalam 72 jam.

---

## 12. Non-Functional Requirements

### 12.1 Performa

| Metrik                           | Target                       | Kondisi                            |
| -------------------------------- | ---------------------------- | ---------------------------------- |
| Waktu respons AI chat            | < 2 detik                    | 95th percentile, koneksi 4G        |
| Waktu deteksi CDS (NLP)          | < 500ms                      | Per pesan, semua level             |
| Notifikasi krisis L3 ke psikolog | < 30 detik                   | Dari deteksi hingga notif terkirim |
| Cold start app (mobile)          | < 3 detik                    | Mid-range device, Android 10+      |
| Latensi voice/video call         | < 150ms                      | WebRTC, jaringan stabil            |
| Throughput concurrent users      | > 10.000 user aktif simultan | Auto-scaling enabled               |
| Pemrosesan EDA (3 modalitas)     | < 3 detik                    | Paralel, per cycle                 |

### 12.2 Keandalan & Ketersediaan

- **Uptime target:** 99.5% per bulan (maksimal ~3.6 jam downtime/bulan)
- **CDS uptime:** 99.9% — komponen ini tidak boleh mati dalam kondisi apapun
- **Database backup:** Real-time replication ke secondary region; RPO < 1 jam; RTO < 4 jam
- **Graceful degradation:** Jika EDA engine down, fitur utama (curhat + konsultasi) tetap berjalan

### 12.3 Skalabilitas

- Arsitektur microservices memungkinkan horizontal scaling per modul secara independen
- AI inference menggunakan auto-scaling GPU cluster (AWS SageMaker / GCP Vertex AI)
- CDN untuk asset statis dan media, mengurangi latensi untuk seluruh ASEAN
- Multi-region cloud deployment (AWS Asia Pacific) untuk acceptable latency di semua ASEAN markets

### 12.4 Kegunaan (Usability)

- UI harus lulus WCAG 2.1 Level AA untuk aksesibilitas
- Onboarding user selesai dalam < 5 menit tanpa bantuan eksternal
- Semua fitur utama dapat diakses maksimal 3 tap dari home screen
- Tersedia dalam Bahasa Indonesia dan Inggris sejak v1.0; ekspansi bahasa ASEAN di v2.0

### 12.5 Kepatuhan Regulasi

| Regulasi                          | Cakupan                                           |
| --------------------------------- | ------------------------------------------------- |
| **UU PDP Indonesia (2024)** | Perlindungan data pribadi, RTBF, data portability |
| **PDPA Thailand**           | User di Thailand                                  |
| **PDPA Singapore**          | User di Singapore                                 |
| **PDP Bill Philippines**    | User di Filipina                                  |
| **Permenkes Telemedicine**  | Layanan konsultasi jarak jauh berbasis teknologi  |
| **STR HIMPSI**              | Verifikasi lisensi psikolog Indonesia             |

---

## 13. UI/UX Requirements

### 13.1 User App (Mobile — Android/iOS)

| Screen               | Deskripsi                        | Fitur Kunci                                                                                                            |
| -------------------- | -------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Splash / Onboarding  | Setup first-time user            | Registrasi, input kontak darurat, persetujuan protokol, EDA consent per modalitas                                      |
| Home Dashboard       | Ringkasan kondisi user           | shortcut "Mulai Curhat", status psikolog terhubung                                                                     |
| Sesi Curhat          | Chat interface dengan AI         | Input teks/voice/gambar, indikator AI listening, emotion badge subtle, tombol "Akhiri Sesi"                            |
| Preview Summary      | Review sebelum kirim ke psikolog | Edit info pribadi, pilih kirim/simpan/hapus, visualisasi emotion timeline                                              |
| Pilih Psikolog       | Marketplace psikolog             | Filter grade/spesialisasi/rating/jadwal, grade badge, profil psikolog                                                  |
| Crisis Screen        | Tampil saat L3 terdeteksi        | Pesan hangat (navy background), hotline 119 ext 8, status psikolog yang dihubungi —**tidak ada tombol dismiss** |
| Konsultasi           | Sesi aktif dengan psikolog       | Chat / Voice / Video toggle, EDA consent toggle, indikator recording                                                   |
| Profil & Settings    | Manajemen akun                   | Kontak darurat, izin EDA per modalitas, privasi, langganan aktif                                                       |
| Riwayat              | Daftar sesi & konsultasi         | Filter, search, dominant emotion per sesi, status summary                                                              |
| Upgrade Subscription | Pilih tier                       | Perbandingan fitur, harga, tombol subscribe ke payment gateway                                                         |

**Prinsip Desain Utama:**

- Seluruh UI menggunakan warna-warna hangat dan menenangkan (tidak ada warna alarm merah di luar Crisis Alert untuk psikolog)
- Language: empatis, tidak klinis, tidak intimidating
- Semua fitur utama maksimal 3 tap dari home screen

---

### 13.2 Professional Dashboard (Web)

| View           | Deskripsi                        | Fitur Kunci                                                       |
| -------------- | -------------------------------- | ----------------------------------------------------------------- |
| Inbox          | Daftar summary masuk             | Badge unread, filter urgensi (CDS level), preview cepat           |
| Summary Detail | Baca summary lengkap klien       | Emotion timeline, kalimat ter-highlight, riwayat interaksi user   |
| EDA Visualizer | Grafik emosi real-time saat sesi | Timeline emosi, VAD chart, ekspresi dominan                       |
| Crisis Alert   | Notifikasi L2/L3                 | Detail pemicu, kalimat trigger, tombol "Respond Now", audit log   |
| Jadwal         | Manajemen ketersediaan           | Kalender, set jam buka, block waktu, timezone auto                |
| Klien          | Daftar user aktif                | Riwayat interaksi, catatan pribadi, progress emosi antar-sesi     |
| Pembayaran     | Laporan keuangan                 | Pendapatan bulan ini, invoice per sesi, permintaan penarikan dana |

---

## 14. External Integrations

| Integrasi                                        | Fungsi                                                | Prioritas |
| ------------------------------------------------ | ----------------------------------------------------- | --------- |
| **OpenAI GPT-4o / GPT-5**                  | LLM untuk S1, S2, S4                                  | Critical  |
| **Google Gemini 1.5 Pro**                  | Fallback LLM                                          | High      |
| **Supabase**                               | PostgreSQL DB + Auth + Realtime + Storage             | Critical  |
| **Firebase Cloud Messaging (FCM)**         | Push notification Android                             | Critical  |
| **Apple Push Notification Service (APNs)** | Push notification iOS                                 | High      |
| **Twilio**                                 | SMS notifikasi kontak darurat                         | High      |
| **WhatsApp Business API**                  | WA notifikasi kontak darurat                          | High      |
| **Midtrans**                               | Payment processing (Indonesia — IDR)                 | Critical  |
| **Stripe**                                 | Payment processing (regional ASEAN)                   | Medium    |
| **LiveKit / Daily.co**                     | WebRTC video/voice call SDK                           | High      |
| **HuggingFace Inference API**              | Hosting IndoBERT, EDA models                          | High      |
| **AWS SageMaker / GCP Vertex AI**          | Model inference auto-scaling                          | Medium    |
| **Into The Light / 119 ext 8**             | Integrasi hotline krisis langsung (jika API tersedia) | High      |

---

## 15. Out of Scope (v1.0)

Fitur-fitur berikut bukan dipotong, melainkan dijadwalkan untuk versi setelah MVP. Ini harus dikomunikasikan secara eksplisit dalam presentasi sebagai roadmap.

| Fitur                                               | Target Versi           |
| --------------------------------------------------- | ---------------------- |
| iOS build                                           | v1.1                   |
| Voice journaling (STT full)                         | v1.1                   |
| Facial expression EDA                               | v1.1                   |
| Live video/voice call (WebRTC penuh)                | v1.1                   |
| Real SMS/WA via Twilio (live, bukan simulated)      | Post-launch            |
| Live payment processing (non-sandbox)               | Post-launch            |
| Custom fine-tuned IndoBERT (hosted)                 | v2.0                   |
| LSTM audio emotion model                            | v2.0                   |
| Multilingual support (Tagalog, Melayu, Thai, Khmer) | v2.0                   |
| Multi-region cloud deployment                       | v2.0 (ASEAN expansion) |
| Institutional integrations (klinik, korporat)       | Year 2                 |
| Peer-reviewed research publications                 | Year 2–3              |

---

## 16. Risks & Mitigations

| Risiko                                                        | Level       | Mitigasi                                                                                                                      |
| ------------------------------------------------------------- | ----------- | ----------------------------------------------------------------------------------------------------------------------------- |
| **CDS false negative** (kasus krisis tidak terdeteksi)  | 🔴 Critical | Multi-layer detection (keyword + contextual BERT + history scoring); target FN <5%; setiap update CDS wajib clinical sign-off |
| **Data breach**                                         | 🔴 Critical | Zero-access E2E encryption; penetration testing pre-launch dan setiap 6 bulan; breach notification protocol 72 jam            |
| **Penyalahgunaan oleh psikolog** (re-identifikasi user) | 🔴 Critical | DPA + NDA legally binding; anonymous alias di summary; audit log akses; mekanisme pelaporan                                   |
| **AI memberikan respons berbahaya**                     | 🔴 Critical | Clinical output validator di semua output S1; CDS override semua respons jika L3; psikolog sign-off semua prompt template     |
| **Regulasi telemedicine berubah**                       | 🟡 Medium   | Legal advisor on-retainer; arsitektur modular memungkinkan penyesuaian cepat                                                  |
| **Low psychologist adoption**                           | 🟡 Medium   | Partnership HIMPSI; onboarding benefit jelas (klien berkualitas, konteks tersedia); tarif kompetitif (70% revenue share)      |
| **User dependency terhadap AI**                         | 🟡 Medium   | AI selalu mendorong koneksi ke psikolog, bukan menggantikannya; batasan tier free mendorong transisi ke care manusia          |
| **GPT-4o API downtime**                                 | 🟡 Medium   | Fallback ke Gemini 1.5 Pro; graceful degradation mode                                                                         |
| **Performa AI dalam bahasa daerah/slang**               | 🟢 Low      | Code-switching detection (FR-CHAT-07); dataset internal dengan contoh bahasa Indonesia urban; ongoing prompt refinement       |

---

## 17. Glossary

| Istilah                            | Definisi                                                                                                                             |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| **User**                     | Pengguna akhir aplikasi Karuna AI yang menggunakan fitur curhat dan konsultasi                                                       |
| **Pro / Professional**       | Psikolog berlisensi HIMPSI atau setara regional ASEAN yang terdaftar dan terverifikasi                                               |
| **Session**                  | Satu sesi curhat antara user dan AI, atau satu sesi konsultasi antara user dan Pro                                                   |
| **Summary**                  | Ringkasan hasil sesi curhat yang dihasilkan AI, siap dikirim ke Pro dengan consent user                                              |
| **EDA**                      | Emotion Detection Analysis: analisis emosi multimodal dari teks, suara, dan ekspresi wajah                                           |
| **CDS**                      | Crisis Detection System: subsistem AI untuk mendeteksi risiko bunuh diri dan self-harm                                               |
| **NLP**                      | Natural Language Processing: pemrosesan teks curhat oleh AI                                                                          |
| **TTS/STT**                  | Text-to-Speech / Speech-to-Text                                                                                                      |
| **SLA**                      | Service Level Agreement: waktu respons maksimum yang dijamin dalam kondisi krisis                                                    |
| **On-Call Pro**              | Psikolog yang sedang bertugas siaga 24/7 untuk penanganan krisis                                                                     |
| **RTBF**                     | Right to Be Forgotten: hak user untuk menghapus semua datanya dari platform                                                          |
| **VAD**                      | Valence-Arousal-Dominance: model tiga dimensi untuk representasi emosi dalam analisis suara                                          |
| **Zero-Access Architecture** | Arsitektur dimana konten sesi dienkripsi sedemikian rupa sehingga bahkan admin platform tidak dapat membacanya                       |
| **STR**                      | Surat Tanda Registrasi: lisensi resmi psikolog dari HIMPSI                                                                           |
| **HIMPSI**                   | Himpunan Psikologi Indonesia: asosiasi psikologi profesional Indonesia                                                               |
| **DPA**                      | Data Processing Agreement: perjanjian legal yang mengikat psikolog dalam menangani data klien                                        |
| **NDA**                      | Non-Disclosure Agreement: perjanjian kerahasiaan untuk interaksi yang dimediasi platform                                             |
| **B2C2B**                    | Business-to-Consumer-to-Business: model bisnis dimana platform melayani konsumen (user) yang kemudian terhubung ke bisnis (psikolog) |

---

*Karuna AI PRD v1.0 — Confidential — Team BaldManAndTwoIdiots*
