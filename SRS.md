# KarunAI

## Emphatic AI Mental Health Bridge Platform

### SOFTWARE REQUIREMENTS SPECIFICATION (SRS)

**Version 1.0 – 2026**

| Dokumen | SOFTWARE REQUIREMENTS SPECIFICATION |
|---------|-------------------------------------|
| Produk  | Karuna AI                           |
| Versi   | 1.0                                 |
| Status  | Draft untuk Direview                |
| Tanggal | 2026                                |

---

## 1. PENGENALAN

Dokumen ini mendefinisikan seluruh persyaratan perangkat lunak untuk Karuna AI, platform kesehatan mental berbasis AI yang menghubungkan pengguna yang membutuhkan dukungan emosional dengan psikolog profesional berlisensi. SRS ini menjadi kontrak teknis antara tim engineering, product, dan pemangku kepentingan lainnya.

KarunAI terdiri dari tiga komponen utama:

- **User App (Android):** Fitur curhat AI, manajemen profil, komunikasi dengan psikolog, dan sistem langganan.
- **Professional Dashboard (Web):** Interface untuk psikolog membaca summary AI, melihat analisis emosi multimodal, dan berkomunikasi dengan klien.
- **AI & Backend Engine:** Sistem NLP untuk analisis curhat, multimodal emotion detection, crisis detection, dan orchestration notifikasi.

### Definisi dan Akronim

| Istilah | Definisi |
|---------|----------|
| User | Pengguna akhir aplikasi Karuna Ai yang menggunakan fitur curhat dan konsultasi |
| Pro / Professional | Psikolog berlisensi yang terdaftar dan terverifikasi di platform |
| Session | Satu sesi curhat antara user dan AI, atau konsultasi antara user dan Pro |
| Summary | Ringkasan hasil sesi curhat yang dihasilkan AI, siap dikirim ke Pro |
| EDA | Emotion Detection Analysis: analisis emosi multimodal dari teks, suara, dan ekspresi wajah |
| CDS | Crisis Detection System: subsistem AI untuk mendeteksi risiko bunuh diri |
| NLP | Natural Language Processing: pemrosesan teks curhat oleh AI |
| TTS/STT | Text-to-Speech / Speech-to-Text |
| SLA | Service Level Agreement: waktu respons maksimum yang dijamin Pro dalam kondisi krisis |
| On-call Pro | Psikolog yang sedang bertugas siaga 24/7 untuk penanganan krisis |

---

## 2. GAMBARAN UMUM

Karuna AI adalah platform B2C2B (Business-to-Consumer-to-Business) yang beroperasi sebagai marketplace berlisensi antara pengguna yang membutuhkan dukungan kesehatan mental dengan psikolog profesional. Platform ini bukan aplikasi terapi mandiri, melainkan infrastruktur jembatan yang meningkatkan aksesibilitas dan efektivitas layanan psikologi yang sudah ada.

### Proposisi Nilai

- **Untuk USER:** Ekspresi emosi bebas tanpa stigma > AI merangkum > Psikolog memahami lebih cepat
- **Untuk PRO:** Konteks klien sudah tersedia sebelum sesi > waktu lebih efisien > penanganan lebih tepat
- **Untuk sistem:** Crisis detection memastikan tidak ada pengguna yang jatuh melalui celah tanpa terdeteksi

### Kelas-kelas User

| Kelas | Deskripsi | Akses | Prioritas |
|-------|-----------|-------|-----------|
| End User | Individu usia 17+ yang mencari dukungan emosional. Tidak harus memiliki diagnosis mental health. | Mobile App Android | Critical |
| Professional (Pro) | Psikolog berlisensi HIMPSI / setara regional ASEAN. Terverifikasi oleh tim Karuna AI. | Web Dashboard + Mobile notif | Critical |
| On-Call Pro | Subset Pro yang terdaftar untuk tugas siaga 24/7 penanganan krisis. | Web Dashboard + Priority notif | Critical |
| Admin | Tim internal CurlyAI untuk verifikasi Pro, moderasi, monitoring sistem. | Admin Panel (Web) | High |
| Emergency Contact | Kontak darurat yang didaftarkan User. Tidak memiliki akun platform. | SMS/WA notifikasi saja | High |

### Lingkungan Operasional

- **User App:** Android 8.0+ (API 26). Minimum RAM 3GB. Koneksi internet diperlukan untuk fitur utama.
- **Professional Dashboard:** Browser modern (Chrome 90+, Firefox 88+, Safari 14+). Desktop-first, responsive untuk tablet.
- **Backend:** Cloud-based (AWS/GCP). Multi-region untuk latensi rendah di Asia Tenggara.
- **Ketersediaan:** 99.5% uptime SLA. Maintenance window maksimal 2 jam/bulan pada dini hari.

### Hal-hal Penting

- Pro yang bergabung wajib memiliki STR (Surat Tanda Registrasi) aktif dari HIMPSI atau badan setara.
- User berusia minimal 17 tahun. User di bawah 18 tahun memerlukan persetujuan orang tua.
- Koneksi internet minimum 1 Mbps untuk fitur voice call; 5 Mbps untuk video call.
- Model AI emotion detection dilatih pada dataset yang mencakup populasi Asia Tenggara.
- Integrasi hotline krisis (Into The Light 119 ext 8) bergantung pada ketersediaan API pihak ketiga.

---

## 3. KEBUTUHAN FUNGSIONAL

### 3.1 Modul Autentikasi dan Onboarding

**FR-AUTH-01 hingga FR-AUTH-06**

| ID | Requirement | Prioritas | Catatan |
|----|-------------|-----------|---------|
| FR-AUTH-01 | Sistem harus mendukung registrasi user via email dan Google OAuth | Critical | — |
| FR-AUTH-02 | Sistem harus melakukan verifikasi email sebelum akun aktif | Critical | — |
| FR-AUTH-03 | User wajib melengkapi onboarding: nama, usia, kontak darurat (min. 1), dan persetujuan protokol krisis | Critical | Tidak bisa skip |
| FR-AUTH-04 | Pro wajib upload STR, foto diri, dan jadwal ketersediaan saat registrasi | Critical | Review admin maks 48 jam |
| FR-AUTH-05 | Sistem harus mendukung autentikasi biometrik (fingerprint/Face ID) untuk login ulang | High | — |
| FR-AUTH-06 | Sistem harus mendukung reset password via email dan verifikasi 2FA | High | — |

### 3.2 Modul Sesi Curhat

**FR-CHAT-01 hingga FR-CHAT-10**

| ID | Requirement | Prioritas | Catatan |
|----|-------------|-----------|---------|
| FR-CHAT-01 | User dapat memulai sesi curhat kapan saja. AI merespons dalam Bahasa Indonesia atau Inggris. | Critical | — |
| FR-CHAT-02 | AI harus merespons dengan empati, tidak memberi diagnosis, tidak memberi solusi medis | Critical | Tone: supportive, non-judgmental |
| FR-CHAT-03 | AI mencatat seluruh percakapan dan menghasilkan summary terstruktur di akhir sesi | Critical | Lihat FR-SUM-01 |
| FR-CHAT-04 | User dapat memilih untuk menutup sesi tanpa membuat summary | High | Data tidak disimpan jika user pilih ini |
| FR-CHAT-05 | AI harus mendukung input teks, voice-to-text, dan gambar (foto ekspresi, drawing) | High | Gambar dianalisis oleh EDA engine |
| FR-CHAT-06 | Sesi curhat harus bisa dilanjutkan (resume) dalam 24 jam jika terputus | High | — |
| FR-CHAT-07 | AI harus bisa mendeteksi bahasa campuran (code-switching Indonesia-Inggris) | Medium | Umum di populasi urban ASEAN |
| FR-CHAT-08 | User dapat melihat riwayat sesi curhat maksimal 90 hari ke belakang | Medium | — |
| FR-CHAT-09 | AI tidak boleh menyimpan konten sesi jika user tidak setuju di onboarding | Critical | GDPR/UU PDP compliance |
| FR-CHAT-10 | Sistem harus menyediakan tombol 'Aku baik-baik saja' untuk menutup sesi dengan cepat tanpa analisis | Medium | Untuk penggunaan singkat |

### 3.3 Modul Summary dan Pengiriman ke Profesional

**FR-SUM-01 hingga FR-SUM-06**

| ID | Requirement | Prioritas | Catatan |
|----|-------------|-----------|---------|
| FR-SUM-01 | AI menghasilkan summary berisi: tema utama, emosi yang terdeteksi, intensitas, pola pikir yang muncul, dan flag risiko jika ada | Critical | — |
| FR-SUM-02 | User melihat preview summary sebelum memutuskan apakah dikirim ke Pro atau tidak | Critical | User bisa edit nama/detail pribadi sebelum kirim |
| FR-SUM-03 | Jika user setuju kirim, sistem menampilkan daftar Pro yang tersedia beserta spesialisasi dan rating | Critical | — |
| FR-SUM-04 | Pro menerima notifikasi push saat summary baru masuk. SLA baca: 24 jam untuk non-krisis | Critical | — |
| FR-SUM-05 | User menerima notifikasi saat Pro telah membaca summary | High | — |
| FR-SUM-06 | Pro memberikan respons awal: rekomendasi (perlu sesi / tidak) + pesan singkat kepada user | Critical | Maks 200 kata |

### 3.4 Modul Konsultasi (Chat/Voice/Video)

**FR-CON-01 hingga FR-CON-08**

| ID | Requirement | Prioritas | Catatan |
|----|-------------|-----------|---------|
| FR-CON-01 | User dapat memilih mode konsultasi: in-app chat, voice call, atau video call | Critical | — |
| FR-CON-02 | Sistem harus menyediakan penjadwalan sesi dengan kalender ketersediaan Pro | Critical | Zona waktu otomatis terdeteksi |
| FR-CON-03 | Sesi video/voice menggunakan enkripsi end-to-end (WebRTC + DTLS-SRTP) | Critical | — |
| FR-CON-04 | Selama sesi berlangsung, EDA engine menganalisis emosi user secara real-time (dengan izin) | High | Hasil tampil di dashboard Pro |
| FR-CON-05 | Pro dapat membuat catatan sesi yang tidak terlihat oleh user | High | — |
| FR-CON-06 | Sistem harus mendukung penjadwalan ulang dengan notifikasi min. 2 jam sebelum sesi | High | — |
| FR-CON-07 | Rekaman sesi (jika diaktifkan) hanya boleh diakses Pro dan user, tidak oleh admin | Critical | Zero-access architecture |
| FR-CON-08 | Setelah sesi selesai, user dapat memberikan rating dan feedback anonim kepada Pro | Medium | — |

### 3.5 Modul Subscription dan Pembayaran

**FR-PAY-01 hingga FR-PAY-05**

| ID | Requirement | Prioritas | Catatan |
|----|-------------|-----------|---------|
| FR-PAY-01 | Sistem mendukung model berlangganan bulanan untuk user dengan tier: Basic, Plus, dan Premium | Critical | Lihat PRD untuk detail tier |
| FR-PAY-02 | Payment gateway: Midtrans (ID), PayMongo (PH), Stripe (regional) | Critical | — |
| FR-PAY-03 | Sistem mengirim invoice digital dan reminder perpanjangan 7 hari sebelum jatuh tempo | High | — |
| FR-PAY-04 | User dapat membatalkan langganan kapan saja. Akses tetap aktif hingga akhir periode | High | — |
| FR-PAY-05 | Pro menerima pembayaran via transfer bank atau e-wallet dengan laporan bulanan otomatis | High | Revenue share 70% Pro / 30% Platform |

### 3.6 Crisis Detection System (CDS)

> **PENTING:**
>
> Seluruh kebutuhan di bagian ini bersifat kritikal dan tidak boleh dikompromikan dalam kondisi apapun. Kegagalan sistem CDS dapat berakibat pada kehilangan nyawa. Setiap perubahan pada modul ini wajib melalui review oleh psikolog klinis senior sebelum dideploy ke production.

#### Klasifikasi Risiko

| Level | Nama | Trigger Indikator | Transparansi ke User |
|-------|------|-------------------|----------------------|
| L1 | Distress | Kesedihan mendalam, hopelessness, kelelahan emosional, isolasi sosial | TRANSPARAN: AI mengakui deteksi, tawari opsi bantuan |
| L2 | At-Risk | Kalimat ambigu tentang kematian, 'lebih baik menghilang', 'semua lebih baik tanpaku' | TERSEMBUNYI: Notif Pro diam-diam, AI lebih aktif tanpa alarming |
| L3 | Crisis | Eksplisit menyebut niat, metode, rencana, atau waktu untuk menyakiti diri sendiri | TRANSPARAN PENUH: User diberitahu bahwa bantuan sedang diaktifkan |

#### Kebutuhan Fungsional CDS

**FR-CDS-01 hingga FR-CDS-12**

| ID | Requirement | Level | Prioritas |
|----|-------------|-------|-----------|
| FR-CDS-01 | NLP engine harus menganalisis setiap pesan user dalam waktu < 500ms untuk deteksi konten berisiko | L1/L2/L3 | Critical |
| FR-CDS-02 | Model CDS harus dikalibrasi untuk false negative rate < 5% (lebih baik over-detect) | L1/L2/L3 | Critical |
| FR-CDS-03 | Saat L3 terdeteksi, sistem WAJIB mengirim notifikasi push ke Pro terhubung dalam < 30 detik | L3 | Critical |
| FR-CDS-04 | Jika Pro tidak respond dalam 5 menit setelah notif L3, sistem otomatis eskalasi ke On-Call Pro | L3 | Critical |
| FR-CDS-05 | Sistem harus menampilkan nomor hotline krisis langsung di layar user saat L3 terdeteksi | L3 | Critical |
| FR-CDS-06 | Kontak darurat user menerima SMS/WA notifikasi saat L3 terdeteksi | L3 | Critical |
| FR-CDS-07 | AI menggunakan kalimat stabilisasi pre-approved (divalidasi psikolog klinis) selama krisis berlangsung | L3 | Critical |
| FR-CDS-08 | AI TIDAK boleh memberikan saran atau informasi apapun yang berpotensi memfasilitasi tindakan menyakiti diri | L1/L2/L3 | Critical |
| FR-CDS-09 | Saat L2 terdeteksi, Pro terhubung menerima notifikasi silent dengan highlight kalimat pemicu | L2 | Critical |
| FR-CDS-10 | Semua event CDS dicatat dalam audit log dengan timestamp, level, tindakan, dan outcome | L1/L2/L3 | Critical |
| FR-CDS-11 | Pro dapat mengubah level risiko user secara manual dari dashboard (upgrade/downgrade) | L1/L2/L3 | High |
| FR-CDS-12 | Setelah insiden L3 selesai, sistem mengirim follow-up check-in otomatis ke user dalam 24 jam | L3 | High |

#### Protokol Eskalasi L3 (Crisis)

| Waktu | | Tindakan |
|-------|---|----------|
| T+00:00 | : | AI deteksi konten L3 > pause conversational mode |
| T+00:05 | : | Tampil pesan stabilisasi pre-approved di layar user |
| T+00:10 | : | Notif push + badge merah ke Pro terhubung |
| T+00:15 | : | Hotline krisis tampil di layar user |
| T+00:20 | : | SMS/WA ke kontak darurat user |
| T+05:00 | : | Jika Pro belum respond > eskalasi ke On-Call Pro (rotasi) |
| T+10:00 | : | Jika On-Call Pro belum respond > notif admin Karuna AI |
| T+15:00 | : | Hard fallback: instruksi langsung hubungi 119 ext 8 atau IGD terdekat |
| Post-event | : | Audit log tersimpan, follow-up check-in dijadwalkan 24 jam kemudian |

### 3.7 Emotion Detection Analysis (EDA) Engine

EDA Engine adalah subsistem AI yang menganalisis emosi user dari tiga modalitas secara paralel dan menghasilkan unified emotion profile yang ditampilkan di Professional Dashboard. EDA bersifat decision-support tool dan tidak pernah menentukan diagnosis.

#### Modalitas Analisis

| Modalitas | Input | Model / Teknik | Output | Akurasi Target |
|-----------|-------|----------------|--------|----------------|
| Analisis Teks (NLP) | Pesan curhat user (teks) | Fine-tuned IndoBERT + sentiment classifier | 7 emosi dasar + intensitas (0–1) | > 80% |
| Analisis Suara | Audio sesi voice/video call (dengan izin) | Acoustic feature extraction + LSTM classifier | Arousal, valence, dominance (VAD model) | > 70% |
| Analisis Ekspresi Wajah | Video frame dari kamera (dengan izin eksplisit) | FER model berbasis MobileNetV3 | 6 ekspresi dasar (Ekman) | > 65% |

#### Kebutuhan Fungsionalitas EDA

| ID | Requirement | Prioritas |
|----|-------------|-----------|
| FR-EDA-01 | Setiap modalitas analisis HARUS mendapat persetujuan eksplisit terpisah dari user di onboarding | Critical |
| FR-EDA-02 | User dapat mencabut izin modalitas tertentu kapan saja dari settings tanpa kehilangan akses layanan | Critical |
| FR-EDA-03 | Hasil EDA ditampilkan di Pro Dashboard sebagai visualisasi grafis, bukan angka mentah | High |
| FR-EDA-04 | EDA harus menyertakan disclaimer yang terlihat: 'Ini adalah estimasi AI, bukan diagnosis klinis' | Critical |
| FR-EDA-05 | Data wajah user tidak boleh disimpan lebih dari durasi sesi — langsung diproses dan di-discard | Critical |
| FR-EDA-06 | EDA harus mampu memproses ketiga modalitas secara paralel dengan latensi total < 3 detik | High |
| FR-EDA-07 | Model EDA harus di-retrain minimal 6 bulan sekali dengan data yang mencakup populasi Asia Tenggara | High |

---

## 4. Kebutuhan Non-Fungsional

### 4.1 Performa

| Metrik | Target | Kondisi |
|--------|--------|---------|
| Waktu respons AI chat | < 2 detik | 95th percentile, koneksi 4G |
| Waktu deteksi CDS (NLP) | < 500ms | Per pesan, semua level |
| Notifikasi krisis L3 ke Pro | < 30 detik | Dari deteksi hingga notif terkirim |
| Cold start app (mobile) | < 3 detik | Mid-range device, Android 10+ |
| Latensi voice/video call | < 150ms | WebRTC, jaringan stabil |
| Throughput concurrent users | > 10.000 user aktif simultan | Auto-scaling enabled |

### 4.2 Privasi dan Keamanan

| Requirement | Standar / Detail |
|-------------|------------------|
| Enkripsi data at-rest | AES-256 untuk semua data user di database |
| Enkripsi data in-transit | TLS 1.3 minimum untuk semua API calls |
| Enkripsi end-to-end sesi | WebRTC + DTLS-SRTP untuk voice/video |
| Enkripsi konten curhat | E2E encryption — backend tidak bisa membaca isi sesi |
| Kepatuhan regulasi | UU PDP Indonesia (2024), PDPA Thailand, PDPA Singapura |
| Hak penghapusan data | User dapat request hapus semua data dalam 30 hari (RTBF) |
| Penetration testing | Wajib dilakukan sebelum launch dan setiap 6 bulan |
| Audit log | Semua akses data sensitif tercatat, retained 2 tahun |

### 4.3 Keandalan dan Ketersediaan

- Uptime target: 99.5% per bulan (maksimal ~3.6 jam downtime/bulan).
- CDS subsystem harus memiliki uptime 99.9% — komponen ini tidak boleh mati.
- Backup database: real-time replication ke secondary region, RPO < 1 jam, RTO < 4 jam.
- Graceful degradation: jika EDA engine down, fitur utama (curhat + konsultasi) tetap berjalan.

### 4.4 Skalabilitas

- Arsitektur microservices memungkinkan scaling horizontal per modul.
- AI inference menggunakan auto-scaling GPU cluster (AWS SageMaker / GCP Vertex AI).
- CDN untuk asset statis dan media, mengurangi latensi untuk pengguna di seluruh ASEAN.

### 4.5 Kegunaan

- UI harus lulus WCAG 2.1 Level AA untuk aksesibilitas.
- Onboarding user selesai dalam < 5 menit tanpa bantuan eksternal.
- Semua fitur utama bisa diakses maksimal 3 tap dari home screen.
- Tersedia dalam Bahasa Indonesia dan Inggris sejak v1.0. Ekspansi bahasa ASEAN di v2.0.

---

## 5. Kebutuhan Antarmuka

### 5.1 User App

| Screen | Deskripsi Singkat | Fitur Kunci |
|--------|-------------------|-------------|
| Splash / Onboarding | First-time user setup | Registrasi, input kontak darurat, persetujuan protokol |
| Home Dashboard | Ringkasan kondisi user | Shortcut curhat, status Pro terhubung |
| Sesi Curhat | Chat interface dengan AI | Input teks/voice, indikator AI listening, tombol akhiri sesi |
| Preview Summary | Review sebelum kirim ke Pro | Edit info pribadi, pilih kirim/simpan/hapus |
| Pilih Profesional | Marketplace Pro | Filter spesialisasi, rating, harga, jadwal tersedia |
| Crisis Screen | Tampil saat L3 terdeteksi | Pesan hangat, hotline, status Pro yang dihubungi |
| Konsultasi | Sesi dengan Pro | Chat / Voice / Video, EDA consent toggle |
| Profil & Settings | Manajemen akun | Kontak darurat, izin EDA, privasi, langganan |
| Riwayat | Daftar sesi & konsultasi | Filter, search, export PDF (opsional) |

### 5.2 Professional Dashboard

| View | Deskripsi Singkat | Fitur Kunci |
|------|-------------------|-------------|
| Inbox | Daftar summary masuk dari user | Badge unread, filter urgensi, preview cepat |
| Summary Detail | Baca summary lengkap | Emosi terdeteksi, highlight kalimat, riwayat user |
| EDA Visualizer | Grafik emosi real-time saat sesi | Timeline emosi, VAD chart, ekspresi dominan |
| Crisis Alert | Notifikasi L2/L3 | Detail pemicu, tombol hubungi sekarang, eskalasi |
| Jadwal | Manajemen ketersediaan | Kalender, set jam buka, block waktu |
| Klien | Daftar user aktif | Riwayat interaksi, catatan pribadi, progress emosi |
| Pembayaran | Laporan keuangan | Pendapatan bulan ini, invoice, penarikan dana |

### 5.3 Antarmuka Eksternal

- **Midtrans/PayMongo/Stripe API:** Pemrosesan pembayaran dan subscription management.
- **Firebase Cloud Messaging (FCM) + APNs:** Push notification untuk iOS dan Android.
- **Twilio/Vonage:** SMS notification untuk kontak darurat (non-app users).
- **WhatsApp Business API:** Notifikasi WA untuk kontak darurat.
- **Into The Light/119 ext 8 API (jika tersedia):** Integrasi hotline krisis langsung.
- **HuggingFace Inference API/AWS SageMaker:** Hosting model AI (NLP, EDA, CDS).
