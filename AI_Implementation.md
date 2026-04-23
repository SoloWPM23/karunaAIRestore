# 🧠 KarunaAI

**Panduan Pengembangan AI Fitur Curhat**
> MVP Prototype + TTS/STT Voice Interface — 100% Free Stack
> Edisi 2.0 — Diperbarui dari Sesi Development Aktual

| Fokus | Stack | GPU | Budget |
|-------|-------|-----|--------|
| AI Curhat + TTS/STT Voice | `google-genai` + Whisper + gTTS | RTX 4050 Laptop (lokal) | Rp 0 — semua gratis |

---

## 📋 Changelog — Apa yang Berubah dari Versi 1.0?

| Area | Versi 1.0 (Lama) | Versi 2.0 (Sekarang) |
|------|------------------|----------------------|
| Library Gemini | `google-generativeai` (deprecated) | `google-genai` (library resmi terbaru) |
| Nama model | `gemini-1.5-flash` | `gemini-2.0-flash` (stabil & gratis) |
| `system_instruction` | Di dalam `generate_content()` | Di dalam `GenerativeModel` constructor |
| `max_output_tokens` | 200 (terlalu kecil, respons terpotong) | 400 (cukup untuk ~150 kata bahasa Indonesia) |
| Training environment | Google Colab | Lokal dengan RTX 4050 (conda myenv) |
| Demo interface | Streamlit dasar | Streamlit + Voice (TTS/STT) |
| Fitur baru | Belum ada | Section 11: TTS/STT Voice Interface |
| `requirements.txt` | `google-generativeai` | `google-genai`, `openai-whisper`, `gTTS` |

---

## 0. Peta Besar: Arsitektur Lengkap

KarunaAI punya 5 komponen utama yang bekerja bersama. Empat subsistem AI inti, ditambah satu layer baru: Voice Interface (TTS/STT).

```
💡 Gambaran Sistem Lengkap (dengan Voice)

USER BICARA (mikrofon)
        ↓
[STT] Whisper — ubah suara → teks
        ↓
[S2] Emotion Engine — deteksi emosi dari teks  ← berjalan PARALEL
[S3] Crisis Detection — deteksi sinyal bahaya  ← berjalan PARALEL
        ↓
[S1] Gemini — hasilkan balasan empatik (teks)
        ↓
[TTS] gTTS/Edge-TTS — ubah teks → suara
        ↓
USER MENDENGAR balasan Karuna
        ↓ (di akhir sesi)
[S4] Summary Generator — ringkasan untuk psikolog
```

### 0.1 Roadmap Pengerjaan (Diperbarui)

| Minggu | Fokus | Output | Status |
|--------|-------|--------|--------|
| Minggu 1 | Setup + S1 dasar | Chatbot teks berjalan di Streamlit | ✅ SELESAI |
| Minggu 2 | S2 — Emotion Engine training | Model emosi berjalan lokal (RTX 4050) | 🔄 Berikutnya |
| Minggu 3 | S3 — Crisis Detection training | Deteksi sinyal bahaya berjalan | ⏳ Menunggu |
| Minggu 4 | S4 + Integrasi Pipeline | End-to-end pipeline terhubung | ⏳ Menunggu |
| Minggu 5 | TTS/STT Voice Interface | User bisa curhat dengan suara | ⏳ Menunggu |
| Minggu 6 | Polish + Demo | Demo lengkap teks + suara | ⏳ Menunggu |

---

## 1. Setup Environment (Diperbarui untuk Lokal + GPU)

Karena menggunakan GPU lokal (RTX 4050), tidak perlu Google Colab. Semua training dan inference bisa dilakukan di mesin sendiri.

### 1.1 Tools yang Dibutuhkan (Semua Gratis)

| Tool | Fungsi | Cara Dapat | Status |
|------|--------|------------|--------|
| Anaconda + myenv | Conda environment dengan PyTorch+CUDA | Sudah ada | ✅ Sudah siap |
| VS Code | IDE development | code.visualstudio.com | ✅ Sudah ada |
| Google Gemini API | LLM untuk S1 dan S4 | aistudio.google.com | ✅ Sudah ada |
| `google-genai` | Library resmi Gemini terbaru | `pip install google-genai` | ✅ Sudah install |
| HuggingFace Hub | Download IndoBERT & simpan model | huggingface.co | Daftar gratis |
| Streamlit | Demo web app | `pip install streamlit` | Sudah install |
| `openai-whisper` | STT: suara → teks (gratis, lokal) | `pip install openai-whisper` | Install minggu 5 |
| gTTS / Edge-TTS | TTS: teks → suara (gratis) | `pip install gtts edge-tts` | Install minggu 5 |
| sounddevice | Rekam suara dari mikrofon | `pip install sounddevice` | Install minggu 5 |

### 1.2 Struktur Folder Proyek (Diperbarui dengan Voice)

```
karunaAI/
├── s1_conversational/
│   ├── gemini_client.py      ← ✅ Sudah selesai (pakai google-genai)
│   ├── prompt_builder.py     ← ✅ Sudah selesai
│   └── output_validator.py   ← ✅ Sudah selesai
├── s2_emotion/
│   ├── data/
│   ├── train_emotion.py      ← 🔄 Minggu 2
│   └── emotion_engine.py     ← 🔄 Minggu 2
├── s3_crisis/
│   ├── data/
│   ├── cds_layer1.py         ← Bisa langsung dipakai (keyword)
│   ├── train_crisis.py       ← Minggu 3
│   └── cds_engine.py         ← Minggu 3
├── s4_summary/
│   └── summary_generator.py  ← Minggu 4
├── voice/                    ← 🆕 Minggu 5 — TTS/STT
│   ├── stt_engine.py         ← Speech-to-Text (Whisper)
│   └── tts_engine.py         ← Text-to-Speech (gTTS/Edge-TTS)
├── pipeline/
│   └── orchestrator.py       ← Minggu 4
├── demo/
│   ├── app.py                ← Demo teks (sedang berjalan)
│   └── app_voice.py          ← 🆕 Demo voice (Minggu 5)
├── models/                   ← Model hasil training tersimpan di sini
├── requirements.txt
└── .env
```

### 1.3 requirements.txt (Diperbarui)

```txt
# requirements.txt — Versi 2.0
# ── Gemini API (WAJIB pakai versi baru ini) ──
google-genai>=0.8.0          # Library resmi terbaru Google GenAI
python-dotenv>=1.0.0

# ── ML & NLP ──────────────────────────────────
torch>=2.2.0                 # Sudah ada di myenv
transformers>=4.40.0
datasets>=2.19.0
sentencepiece>=0.2.0
scikit-learn>=1.4.0
accelerate>=0.30.0
numpy>=1.26.0
pandas>=2.2.0
protobuf==3.20.3             # Fix konflik protobuf dengan transformers

# ── Demo Interface ────────────────────────────
streamlit>=1.35.0

# ── Voice (install saat Minggu 5) ─────────────
# openai-whisper    # STT: suara → teks
# gtts              # TTS: teks → suara (simpel)
# edge-tts          # TTS: teks → suara (lebih natural)
# sounddevice       # Rekam audio dari mikrofon
# scipy             # Proses audio
```

---

## 2. S1 — Conversational LLM ✅ Sudah Selesai

> **Status: SELESAI**
> S1 sudah berjalan dengan baik. Ringkasan konfigurasi yang benar:
> - **Library**: `google-genai` (BUKAN `google-generativeai` yang lama)
> - **Model**: `gemini-2.0-flash`
> - **`max_output_tokens`**: 400 (bukan 200 — terlalu kecil untuk bahasa Indonesia)
> - **`system_instruction`**: diletakkan di `GenerateContentConfig`, BUKAN di constructor

### 2.1 gemini_client.py — Versi Final

```python
# s1_conversational/gemini_client.py — VERSI FINAL ✅
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def chat_with_gemini(system_prompt: str, history: list, user_message: str) -> str:
    contents = history + [
        types.Content(role="user", parts=[types.Part(text=user_message)])
    ]
    response = client.models.generate_content(
        model="gemini-2.0-flash",   # ← lowercase semua, bukan "Gemini-2.0-Flash"
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            max_output_tokens=400,  # ← 400, bukan 200 (bahasa ID butuh lebih banyak token)
            temperature=0.7,
        )
    )
    return response.text or ""
```

### 2.2 Pelajaran dari Debugging

| Error yang Ditemui | Penyebab | Solusi |
|--------------------|----------|--------|
| `system_instruction` unexpected keyword | Library lama tidak support parameter ini | Upgrade ke `google-genai` terbaru |
| `models/gemini-1.5-flash` not found | Format nama model salah | Pakai `"gemini-2.0-flash"` (lowercase) |
| API Key not found | Dua library konflik (`generativeai` + `genai`) | Uninstall `google-generativeai`, pakai `google-genai` |
| Respons terpotong di tengah kalimat | `max_output_tokens=200` terlalu kecil | Naikkan ke 400 atau lebih |
| `ModuleNotFoundError s1_conversational` | Dijalankan dari dalam folder `demo/` | Selalu jalankan dari root folder `karunaAI/` |
| `TypeError protobuf` | Konflik versi protobuf | `pip install protobuf==3.20.3` |
| `streamlit not recognized` | Streamlit belum install / env belum aktif | `pip install streamlit`, gunakan `python -m streamlit` |

---

## 3. S2 — Emotion Engine (Minggu 2 — Training Lokal)

> **Apa ini?** Model ML yang dilatih sendiri untuk mendeteksi emosi dari teks curhat.
> Basis: IndoBERT (BERT khusus bahasa Indonesia) + Multi-head classification.
> Output: `dominant_emotion`, `emotion_score`, `topics`, `distress_score`

### 3.1 Konsep: IndoBERT + Transfer Learning

- **Transfer Learning**: Ambil IndoBERT yang sudah "pintar" berbahasa Indonesia, lalu tambahkan classification head. Yang dilatih hanya head-nya — bukan seluruh model dari nol.
- **Multi-head Classification**: Satu model, dua output sekaligus (emosi + topik). Lebih efisien dari dua model terpisah.
- **[CLS] Token**: Token pertama dalam setiap input BERT yang merangkum makna seluruh kalimat. Representasinya (768 dimensi) dimasukkan ke classification head.

### 3.2 Dataset yang Digunakan

| Dataset | Sumber | Ukuran | Label | Cara Download |
|---------|--------|--------|-------|---------------|
| EmoSet-ID | github.com/indonlp/EmoSet | ~3.500 | 7 emosi | `git clone` atau download ZIP |
| IndoNLU SMSA | github.com/IndoNLP/indlu | ~11.000 | pos/neg/netral | `pip install indobenchmark-toolkit` |
| Simulasi curhat | Buat manual / generate dengan Gemini | ~200 | Semua label | Buat sendiri (lihat 3.2.1) |

> **💡 Tips: Buat Data Simulasi dengan Gemini**
> Daripada mengumpulkan data nyata (perlu consent, privasi, dll), generate data simulasi menggunakan Gemini:
> *"Buatkan 20 contoh kalimat curhat dalam bahasa Indonesia yang mengekspresikan emosi SEDIH dengan topik PEKERJAAN. Variasikan gaya bahasa (formal, informal, slang). Format: satu kalimat per baris."*
> Lakukan ini untuk setiap kombinasi emosi × topik → dapat ratusan data dalam hitungan menit.

### 3.3 Script Training Lokal (RTX 4050)

```python
# s2_emotion/train_emotion.py
# Jalankan: python s2_emotion/train_emotion.py (dari root karunaAI/)

import torch
from transformers import AutoTokenizer, AutoModel, TrainingArguments, Trainer
from torch import nn
from datasets import Dataset
import pandas as pd
from sklearn.metrics import f1_score
import numpy as np

# Cek GPU — harus True dengan RTX 4050
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Device: {device} — {torch.cuda.get_device_name(0) if device=='cuda' else 'CPU'}")

EMOTION_LABELS = {0:"joy", 1:"sadness", 2:"anger", 3:"fear", 4:"surprise", 5:"disgust", 6:"neutral"}
TOPIC_LABELS   = {0:"work", 1:"relationship", 2:"family", 3:"health", 4:"finance", 5:"self", 6:"other"}

# ── Model ────────────────────────────────────────────────────────────────
class EmotionModel(nn.Module):
    def __init__(self, n_emotions=7, n_topics=7):
        super().__init__()
        self.encoder = AutoModel.from_pretrained("indolem/indobert-base-uncased")
        self.dropout = nn.Dropout(0.3)
        # Head A: 768 (IndoBERT output) → 256 → 7 (emosi)
        self.emotion_head = nn.Sequential(
            nn.Linear(768, 256), nn.ReLU(), nn.Dropout(0.2), nn.Linear(256, n_emotions)
        )
        # Head B: 768 → 128 → 7 (topik)
        self.topic_head = nn.Sequential(
            nn.Linear(768, 128), nn.ReLU(), nn.Linear(128, n_topics)
        )

    def forward(self, input_ids, attention_mask, labels=None):
        out = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        cls_emb = self.dropout(out.last_hidden_state[:, 0, :])  # [CLS] token
        emotion_logits = self.emotion_head(cls_emb)
        topic_logits   = self.topic_head(cls_emb)
        loss = None
        if labels is not None:
            ce = nn.CrossEntropyLoss()
            loss = ce(emotion_logits, labels["emotion"]) * 0.7 \
                 + ce(topic_logits,   labels["topic"])   * 0.3
        return {"loss": loss, "emotion": emotion_logits, "topic": topic_logits}

# ── Training Config ──────────────────────────────────────────────────────
# fp16=True memanfaatkan Tensor Cores di RTX 4050 → training ~2x lebih cepat
training_args = TrainingArguments(
    output_dir="./models/emotion_engine",
    num_train_epochs=8,
    per_device_train_batch_size=16,   # Sesuaikan jika VRAM penuh (turunkan ke 8)
    per_device_eval_batch_size=32,
    learning_rate=2e-5,
    weight_decay=0.01,
    warmup_ratio=0.1,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    fp16=True,                        # Mixed precision — butuh CUDA
    dataloader_num_workers=0,         # Windows: selalu 0 untuk hindari error
    report_to="none",                 # Matikan wandb/tensorboard
)
```

> ⚠️ **Catatan Penting untuk Windows + RTX 4050**
> - `dataloader_num_workers` HARUS = 0 di Windows. Nilai > 0 akan menyebabkan `RuntimeError`.
> - `fp16=True` membutuhkan CUDA. RTX 4050 support CUDA, jadi ini aman dan training ~2x lebih cepat.

### 3.4 emotion_engine.py — Inference

```python
# s2_emotion/emotion_engine.py
import torch
from transformers import AutoTokenizer
from dataclasses import dataclass

EMOTION_LABELS = {0:"joy",1:"sadness",2:"anger",3:"fear",4:"surprise",5:"disgust",6:"neutral"}
TOPIC_LABELS   = {0:"work",1:"relationship",2:"family",3:"health",4:"finance",5:"self",6:"other"}

@dataclass
class EmotionData:
    dominant      : str    # Emosi dominan, misal "sadness"
    score         : float  # Probabilitas 0.0-1.0
    distribution  : dict   # Semua emosi + probabilitasnya
    topics        : list   # Topik yang terdeteksi (prob > 0.3)
    distress_score: float  # Gabungan sadness + anger + fear

class EmotionEngine:
    def __init__(self, model_path: str):
        self.tokenizer = AutoTokenizer.from_pretrained("indolem/indobert-base-uncased")
        self.model = torch.load(f"{model_path}/emotion_model.pt", map_location="cuda")
        self.model.eval()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)

    def analyze(self, text: str) -> EmotionData:
        inputs = self.tokenizer(text, max_length=256, padding="max_length",
                                truncation=True, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = self.model(**inputs)
        emotion_probs = torch.softmax(outputs["emotion"], dim=-1)[0]
        topic_probs   = torch.softmax(outputs["topic"],   dim=-1)[0]
        dominant_idx  = emotion_probs.argmax().item()
        distress      = (emotion_probs[1] + emotion_probs[2] + emotion_probs[3]).item()
        topics        = [TOPIC_LABELS[i] for i, prob in enumerate(topic_probs) if prob > 0.3]
        return EmotionData(
            dominant=EMOTION_LABELS[dominant_idx],
            score=emotion_probs[dominant_idx].item(),
            distribution={EMOTION_LABELS[i]: p.item() for i, p in enumerate(emotion_probs)},
            topics=topics if topics else ["other"],
            distress_score=distress
        )
```

---

## 4. S3 — Crisis Detection System (Minggu 3)

> 🚨 **Komponen Paling Kritis**
> Setiap perubahan pada CDS WAJIB dipikirkan dengan sangat hati-hati.
> False negative (miss krisis nyata) jauh lebih berbahaya dari false positive.
> **Target: Recall kelas crisis > 85%.**
> Untuk MVP: Layer 1 (keyword) bisa langsung dipakai tanpa training.

### 4.1 Arsitektur 3 Layer

| Layer | Teknik | Waktu | Kapan Bisa Dipakai |
|-------|--------|-------|--------------------|
| Layer 1 | Keyword + Regex | < 10ms | Sekarang — tidak butuh training |
| Layer 2 | Fine-tuned IndoBERT | < 300ms | Setelah training Minggu 3 |
| Layer 3 | History trend analysis | < 200ms | Setelah S2 selesai (butuh `distress_score`) |

### 4.2 cds_layer1.py — Bisa Langsung Dipakai

```python
# s3_crisis/cds_layer1.py
import re

KEYWORDS_L3 = [
    r"\b(bunuh diri|mau bunuh diri)\b",
    r"\b(mau mati|pengen mati|ingin mati)\b",
    r"\b(tidak mau hidup|gak mau hidup|udah gak mau hidup)\b",
    r"\b(akhiri hidup|akhiri segalanya|mengakhiri hidup)\b",
    r"\b(sudah tidak ada gunanya aku|gak ada gunanya lagi)\b",
]

KEYWORDS_L2 = [
    r"\b(sudah tidak tahan|udah gak tahan|gak sanggup lagi)\b",
    r"\b(tidak ada harapan|gak ada harapan|udah gak ada harapan)\b",
    r"\b(semua salahku|semua kesalahanku|ini salah aku semua)\b",
    r"\b(tidak ada yang peduli|gak ada yang peduli|ga ada yg peduli)\b",
    r"\b(jadi beban|beban buat semua|cuma jadi beban)\b",
]

KEYWORDS_L1 = [
    r"\b(sangat lelah|kelelahan|udah capek banget)\b",
    r"\b(tidak berharga|gak berharga|merasa gak berharga)\b",
    r"\b(tidak berguna|gak berguna|merasa gak berguna)\b",
    r"\b(menyesal lahir|nyesal hidup)\b",
]

def layer1_detect(text: str) -> tuple[str, float]:
    text_lower = text.lower()
    for pattern in KEYWORDS_L3:
        if re.search(pattern, text_lower): return "L3", 0.95
    for pattern in KEYWORDS_L2:
        if re.search(pattern, text_lower): return "L2", 0.80
    for pattern in KEYWORDS_L1:
        if re.search(pattern, text_lower): return "L1", 0.60
    return "NORMAL", 0.05
```

### 4.3 cds_engine.py — Aggregator

```python
# s3_crisis/cds_engine.py
from dataclasses import dataclass
from s3_crisis.cds_layer1 import layer1_detect

@dataclass
class CDSResult:
    level   : str    # "NORMAL", "L1", "L2", "L3"
    score   : float  # Skor agregat 0.0-1.0
    triggers: list   # Apa yang memicu

def analyze_crisis(text: str, emotion_history: list = []) -> CDSResult:
    level_kw, conf_kw = layer1_detect(text)

    if level_kw == "L3":
        return CDSResult(level="L3", score=0.95, triggers=["L3_keyword"])

    hist_score = 0.0
    if len(emotion_history) >= 3:
        last_3 = [e.distress_score for e in emotion_history[-3:]]
        if last_3[2] > last_3[1] > last_3[0]:
            hist_score = 0.3

    level_to_score = {"NORMAL":0.05, "L1":0.35, "L2":0.65, "L3":0.90}
    final_score    = level_to_score[level_kw] * conf_kw * 0.70 + hist_score * 0.30

    if   final_score >= 0.75: level = "L3"
    elif final_score >= 0.45: level = "L2"
    elif final_score >= 0.20: level = "L1"
    else:                     level = "NORMAL"

    return CDSResult(level=level, score=final_score, triggers=[level_kw])
```

---

## 5. S4 — Summary Generator (Minggu 4)

> **Apa ini?** Dijalankan SATU KALI di akhir sesi, menggunakan Gemini untuk merangkum seluruh percakapan + data emosi dari S2 menjadi dokumen terstruktur untuk psikolog.

```python
# s4_summary/summary_generator.py
from s1_conversational.gemini_client import chat_with_gemini

SUMMARY_PROMPT = """
Kamu adalah asisten analisis klinis untuk psikolog profesional.
Buat ringkasan terstruktur dari sesi curhat berikut.

## RINGKASAN SESI
**Jumlah pesan**: [angka]
**Emosi Dominan**: [emosi paling sering muncul]
**Level Distress**: [Rendah / Sedang / Tinggi]

## TOPIK UTAMA
[2-3 topik yang paling banyak dibahas]

## PERJALANAN EMOSI
[Apakah emosi membaik, memburuk, atau fluktuatif sepanjang sesi?]

## KUTIPAN PENTING (verbatim dari user)
[2-3 kutipan yang paling relevan secara klinis]

## CATATAN UNTUK PSIKOLOG
[Hal spesifik yang perlu diperhatikan di sesi pertama]

PENTING: JANGAN berikan diagnosis. Gunakan bahasa deskriptif.
"""

def generate_summary(transcript: list, emotion_timeline: list) -> str:
    transcript_text = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in transcript])
    emotion_text    = "\n".join([
        f"Pesan {i+1}: {e.dominant} ({e.score:.0%}), distress={e.distress_score:.2f}"
        for i, e in enumerate(emotion_timeline)
    ])
    prompt = f"TRANSKRIP:\n{transcript_text}\n\nDATA EMOSI:\n{emotion_text}"
    return chat_with_gemini(SUMMARY_PROMPT, [], prompt)
```

---

## 6. Pipeline Integrasi — Orchestrator (Minggu 4)

```python
# pipeline/orchestrator.py
import asyncio
from dataclasses import dataclass, field
from google.genai import types
from s1_conversational.prompt_builder import build_system_prompt
from s1_conversational.gemini_client   import chat_with_gemini
from s1_conversational.output_validator import validate
from s2_emotion.emotion_engine  import EmotionEngine
from s3_crisis.cds_engine       import analyze_crisis

@dataclass
class Session:
    session_id     : str
    messages       : list = field(default_factory=list)  # History Gemini
    chat_log       : list = field(default_factory=list)  # History UI
    emotion_history: list = field(default_factory=list)  # EmotionData per pesan

class KarunaOrchestrator:
    def __init__(self, model_path: str):
        self.emotion_engine = EmotionEngine(model_path)

    async def process_message(self, session: Session, user_message: str) -> dict:
        # STEP 1: Jalankan S2 dan S3 paralel
        emotion_task = asyncio.create_task(asyncio.to_thread(self.emotion_engine.analyze, user_message))
        cds_task     = asyncio.create_task(asyncio.to_thread(analyze_crisis, user_message, session.emotion_history))
        emotion_data, cds_result = await asyncio.gather(emotion_task, cds_task)

        # STEP 2: Build prompt dengan konteks S2+S3
        system_prompt = build_system_prompt(
            dominant_emotion=emotion_data.dominant, emotion_score=emotion_data.score,
            cds_level=cds_result.level, message_count=len(session.messages),
            topics=emotion_data.topics
        )

        # STEP 3: Kirim ke Gemini (S1)
        ai_response = chat_with_gemini(system_prompt, session.messages, user_message)

        # STEP 4: Validasi
        is_valid, reason = validate(ai_response)
        if not is_valid:
            correction_msg = types.Content(role="model",
                parts=[types.Part(text=f"Respons tidak valid: {reason}. Tulis ulang.")])
            session.messages.append(correction_msg)
            ai_response = chat_with_gemini(system_prompt, session.messages, user_message)

        # STEP 5: Update state
        session.messages.append(types.Content(role="user",  parts=[types.Part(text=user_message)]))
        session.messages.append(types.Content(role="model", parts=[types.Part(text=ai_response)]))
        session.chat_log.append({"role":"user",  "content":user_message})
        session.chat_log.append({"role":"model", "content":ai_response})
        session.emotion_history.append(emotion_data)

        # STEP 6: Crisis protocol
        if cds_result.level == "L3":
            ai_response += "\n\n⚠️ Jika kamu dalam bahaya sekarang, hubungi Into The Light: 119 ext 8"

        return {"ai_response":ai_response, "emotion":emotion_data, "cds":cds_result}
```

---

## 7. Demo App — Streamlit ✅ Sudah Berjalan

### 7.1 demo/app.py — Versi Final

```python
# demo/app.py — VERSI FINAL ✅
# Jalankan: python -m streamlit run demo/app.py (dari root karunaAI/)

import streamlit as st
import uuid
from google.genai import types
from s1_conversational.prompt_builder   import build_system_prompt
from s1_conversational.gemini_client    import chat_with_gemini
from s1_conversational.output_validator import validate

st.set_page_config(page_title="KarunaAI Demo", page_icon="🧠")
st.title("🧠 KarunaAI — Demo Fitur Curhat")
st.caption("Prototype MVP — S2/S3 dummy, akan diintegrasikan setelah training")

if "messages" not in st.session_state:
    st.session_state.messages  = []
    st.session_state.chat_log  = []
    st.session_state.msg_count = 0

for msg in st.session_state.chat_log:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if user_input := st.chat_input("Ceritakan apa yang kamu rasakan..."):
    st.session_state.msg_count += 1
    with st.chat_message("user"):
        st.write(user_input)

    system_prompt = build_system_prompt(
        dominant_emotion="neutral", emotion_score=0.5,
        cds_level="NORMAL", message_count=st.session_state.msg_count,
        topics=["general"]
    )

    with st.spinner("Karuna sedang mendengarkan..."):
        ai_response = chat_with_gemini(system_prompt, st.session_state.messages, user_input)

    is_valid, reason = validate(ai_response)
    with st.chat_message("assistant"):
        st.write(ai_response)
        if not is_valid: st.caption(f"⚠️ Validator: {reason}")

    st.session_state.messages.append(types.Content(role="user",  parts=[types.Part(text=user_input)]))
    st.session_state.messages.append(types.Content(role="model", parts=[types.Part(text=ai_response)]))
    st.session_state.chat_log.append({"role":"user",      "content":user_input})
    st.session_state.chat_log.append({"role":"assistant", "content":ai_response})

    with st.sidebar:
        st.subheader("📊 Debug Info")
        st.metric("Pesan ke-", st.session_state.msg_count)
        st.metric("Validator", "✅ OK" if is_valid else f"❌ {reason}")
        st.info("S2 Emotion: dummy\nS3 CDS: dummy")
```

> ▶️ **Cara Menjalankan**: Selalu dari root folder `karunaAI/`:
> ```bash
> python -m streamlit run demo/app.py
> ```
> Browser akan terbuka otomatis di `localhost:8501`.

---

## 8. Evaluasi Model (Perspektif Data Scientist)

### 8.1 Metrik untuk S2 — Emotion Engine

Gunakan F1-Score per kelas, bukan akurasi — karena distribusi emosi sangat imbalanced.

```python
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

y_true = [...]  # Label asli
y_pred = [...]  # Prediksi model

print(classification_report(y_true, y_pred, target_names=list(EMOTION_LABELS.values())))

cm = confusion_matrix(y_true, y_pred)
sns.heatmap(cm, annot=True, xticklabels=EMOTION_LABELS.values(),
                            yticklabels=EMOTION_LABELS.values())
plt.savefig("confusion_matrix.png")

# Target MVP:
# F1 macro-average > 0.65
# F1 kelas "sadness" > 0.70 (paling kritis)
```

### 8.2 Troubleshooting Training

| Masalah | Penyebab | Solusi |
|---------|----------|--------|
| Loss tidak turun sama sekali | Learning rate terlalu besar | Turunkan dari `2e-5` → `5e-6` |
| Overfitting (train bagus, val buruk) | Data terlalu sedikit | Tambah data augmentasi atau turunkan epoch |
| Semua prediksi kelas yang sama | Data sangat imbalanced | Tambah `class_weight` di `CrossEntropyLoss` |
| CUDA out of memory | Batch size terlalu besar | Turunkan `per_device_train_batch_size` dari 16 → 8 |
| RuntimeError multiprocessing | `num_workers > 0` di Windows | Set `dataloader_num_workers=0` |
| F1 rendah di kelas tertentu | Data kelas itu sedikit | Oversample kelas tersebut sebelum training |

---

## 9. TTS/STT — Voice Interface 🆕 (Minggu 5)

> **Apa ini?** Setelah S1-S4 berjalan, tambahkan kemampuan voice:
> - **STT (Speech-to-Text)**: User bicara → teks (Whisper dari OpenAI — GRATIS & lokal)
> - **TTS (Text-to-Speech)**: Teks balasan → suara Karuna (Edge-TTS — GRATIS)
> Whisper berjalan 100% lokal di GPU (RTX 4050) — tidak perlu internet, tidak ada biaya.

### 9.1 Install Dependencies Voice

```bash
pip install openai-whisper   # STT — model Whisper (gratis, lokal)
pip install edge-tts         # TTS — suara Microsoft (gratis, butuh internet)
pip install gtts             # TTS alternatif — Google TTS
pip install sounddevice      # Rekam audio dari mikrofon
pip install scipy            # Proses file audio

# Download model Whisper sekali saja:
python -c "import whisper; whisper.load_model('base')"
# "base"  = 74MB,  cukup akurat untuk bahasa Indonesia
# "small" = 244MB, lebih akurat tapi lebih lambat
```

### 9.2 Perbandingan Opsi TTS

| Library | Kualitas Suara | Kecepatan | Koneksi | Bahasa Indonesia | Rekomendasi |
|---------|---------------|-----------|---------|-----------------|-------------|
| gTTS | Cukup baik | Lambat (API call) | Internet | ✅ Ada | Backup |
| Edge-TTS | Sangat natural | Cepat | Internet | ✅ Ada (id-ID) | ⭐ Utama |
| pyttsx3 | Kurang natural | Sangat cepat | Offline | ⚠️ Terbatas | Fallback offline |

### 9.3 voice/stt_engine.py — Speech to Text

```python
# voice/stt_engine.py — berjalan 100% lokal di GPU
import whisper
import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np, tempfile, os

whisper_model = whisper.load_model("base")

def record_audio(duration_seconds: int = 10, sample_rate: int = 16000) -> str:
    """Rekam audio dari mikrofon. Returns: path ke file .wav sementara."""
    print(f"🎙️ Merekam selama {duration_seconds} detik...")
    audio = sd.rec(int(duration_seconds * sample_rate), samplerate=sample_rate,
                   channels=1, dtype="float32")
    sd.wait()
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    wav.write(tmp.name, sample_rate, (audio * 32767).astype(np.int16))
    return tmp.name

def transcribe(audio_path: str) -> str:
    """Ubah file audio → teks menggunakan Whisper."""
    result = whisper_model.transcribe(audio_path, language="id", fp16=True)
    os.unlink(audio_path)
    return result["text"].strip()

def record_and_transcribe(duration_seconds: int = 10) -> str:
    """One-shot: rekam lalu langsung transcribe."""
    return transcribe(record_audio(duration_seconds))
```

### 9.4 voice/tts_engine.py — Text to Speech

```python
# voice/tts_engine.py — menggunakan Edge-TTS untuk suara paling natural
import edge_tts, asyncio, tempfile, os
import sounddevice as sd, scipy.io.wavfile as wav

# id-ID-ArdiNeural  → suara laki-laki
# id-ID-GadisNeural → suara perempuan ← REKOMENDASI untuk Karuna
VOICE = "id-ID-GadisNeural"

async def _speak_async(text: str, voice: str = VOICE):
    communicate = edge_tts.Communicate(text, voice)
    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    await communicate.save(tmp.name)
    return tmp.name

def speak(text: str, voice: str = VOICE):
    """Ubah teks → suara dan mainkan langsung. Blocking."""
    audio_path = asyncio.run(_speak_async(text, voice))
    sample_rate, data = wav.read(audio_path)
    sd.play(data, sample_rate)
    sd.wait()
    os.unlink(audio_path)

def speak_to_file(text: str, output_path: str, voice: str = VOICE):
    """Simpan audio ke file (berguna untuk Streamlit)."""
    asyncio.run(_speak_async(text, voice))
```

### 9.5 Test Voice Pipeline

```python
# test_voice.py
# Test TTS dulu (tidak butuh mikrofon):
from voice.tts_engine import speak
speak("Halo, aku Karuna. Aku di sini untuk mendengarkan kamu.")

# Test STT (butuh mikrofon):
# from voice.stt_engine import record_and_transcribe
# text = record_and_transcribe(duration_seconds=5)
# print(f"Kamu berkata: {text}")
```

> 📱 **Catatan: Rekam Langsung di Browser**
> Streamlit belum support rekam mikrofon secara native.
> - **Opsi A** (lebih mudah): User rekam dulu di HP/PC → save → upload ke app.
> - **Opsi B** (lebih canggih): Gunakan library `streamlit-webrtc` untuk rekam langsung.
> Untuk lomba/demo, Opsi A sudah cukup mengesankan.

---

## 10. Urutan Pengerjaan Lengkap

### ✅ Minggu 1 — SELESAI
- [x] Setup conda env (myenv) + VS Code
- [x] Install `google-genai` (library baru)
- [x] Dapatkan Gemini API Key
- [x] Buat `gemini_client.py`, `prompt_builder.py`, `output_validator.py`
- [x] Fix: model name lowercase, `max_output_tokens=400`, `protobuf==3.20.3`
- [x] `test_gemini.py` berhasil → Karuna merespons dengan empati
- [x] `test_pipeline.py` Valid: True | OK
- [x] `demo/app.py` berjalan di browser

### 🔄 Minggu 2 — Berikutnya: S2 Emotion Engine
1. Buat folder `s2_emotion/data/`
2. Download EmoSet-ID: `git clone https://github.com/indonlp/EmoSet`
3. Generate data simulasi dengan Gemini (lihat Section 3.2)
4. Jalankan `train_emotion.py` dari root folder (bukan dari dalam `s2_emotion/`)
5. Monitor: loss turun tiap epoch, F1 naik
6. Simpan model terbaik ke `models/emotion_engine/`
7. Test `emotion_engine.py` dengan beberapa kalimat
8. Update `app.py`: ganti nilai dummy dengan output `EmotionEngine`

### ⏳ Minggu 3 — S3 Crisis Detection
1. Kumpulkan data crisis (dataset publik + generate dengan Gemini)
2. Integrasikan `cds_layer1.py` (keyword) langsung — tidak butuh training
3. Training model Layer 2 dengan arsitektur mirip S2
4. Evaluasi: pastikan Recall crisis > 85%
5. Integrasikan ke `app.py`

### ⏳ Minggu 4 — S4 + Integrasi Pipeline
1. Buat `summary_generator.py`
2. Buat `orchestrator.py` (menggabungkan S1+S2+S3+S4)
3. Update `app.py`: pakai orchestrator, tambah tombol "Akhiri Sesi"
4. End-to-end test: simulasikan sesi curhat penuh

### ⏳ Minggu 5 — Voice Interface (TTS/STT)
1. Install: `pip install openai-whisper edge-tts sounddevice scipy`
2. Download model Whisper: `python -c "import whisper; whisper.load_model('base')"`
3. Buat `stt_engine.py` dan `tts_engine.py`
4. Test TTS dulu (`python test_voice.py`)
5. Test STT dengan rekaman suara
6. Buat `app_voice.py` (Streamlit dengan tab teks + suara)

### ⏳ Minggu 6 — Polish & Demo
1. End-to-end test seluruh pipeline teks + suara
2. Edge case testing: slang, typo, bahasa campur
3. Evaluasi ulang S3 dengan kalimat krisis simulasi
4. Deploy ke Streamlit Community Cloud (gratis) untuk akses publik
5. Siapkan demo script untuk presentasi lomba

---

## 11. Glossary — Kamus Istilah

| Istilah | Penjelasan Sederhana |
|---------|---------------------|
| API / API Key | "Menu restoran" untuk berkomunikasi antar program. Key = password akses. |
| `google-genai` | Library Python resmi terbaru dari Google untuk mengakses Gemini API. |
| BERT / IndoBERT | Model bahasa yang memahami teks dua arah. IndoBERT = versi khusus bahasa Indonesia. |
| Transfer Learning | Pakai model yang sudah "pintar" sebagai fondasi, lalu latih untuk tugas spesifik. |
| Fine-tuning | Melatih ulang sebagian kecil model yang sudah ada dengan data domain kita. |
| Multi-head Classification | Satu model menghasilkan beberapa output sekaligus (emosi + topik). |
| [CLS] Token | Token pertama BERT yang merangkum makna seluruh kalimat. |
| Embedding | Representasi teks sebagai vektor angka. Teks serupa → vektor berdekatan. |
| Logits | Output mentah model sebelum diubah jadi probabilitas. Bisa negatif. |
| Softmax | Fungsi yang ubah logits → probabilitas (semua positif, jumlah = 1.0). |
| Loss / CrossEntropyLoss | Seberapa salah prediksi model. Tujuan training: minimisasi loss. |
| Epoch | Satu kali model melihat seluruh dataset. 8 epoch = dataset dilihat 8x. |
| Batch Size | Jumlah sampel diproses sekaligus. Lebih besar = lebih cepat tapi butuh VRAM lebih. |
| Learning Rate | Seberapa besar update bobot per step. Terlalu besar = tidak stabil. |
| fp16 / Mixed Precision | Training dengan 16-bit float → 2x lebih cepat di GPU modern seperti RTX 4050. |
| Dropout | Matikan neuron secara acak saat training untuk mencegah overfitting. |
| Overfitting | Model hafal training data tapi gagal generalisasi ke data baru. |
| F1-Score | Rata-rata harmonik Precision dan Recall. Ideal untuk data imbalanced. |
| Recall | Dari semua positif nyata, berapa % yang berhasil terdeteksi. |
| Precision | Dari semua yang diprediksi positif, berapa % yang benar-benar positif. |
| Prompt Engineering | Menulis instruksi yang tepat untuk LLM agar menghasilkan output yang diinginkan. |
| Few-Shot Learning | Memberikan beberapa contoh dalam prompt untuk mengkalibrasi perilaku LLM. |
| STT (Speech-to-Text) | Mengubah audio suara manusia menjadi teks. Menggunakan Whisper (lokal, gratis). |
| TTS (Text-to-Speech) | Mengubah teks menjadi suara sintetis. Menggunakan Edge-TTS (gratis, natural). |
| Whisper | Model STT open-source dari OpenAI. Berjalan lokal di GPU. Support bahasa Indonesia. |
| Edge-TTS | Library TTS gratis menggunakan infrastruktur Microsoft. Suara sangat natural. |
| Streamlit | Library Python untuk buat web app interaktif dengan cepat — ideal untuk demo ML. |
| asyncio | Cara Python menjalankan beberapa tugas bersamaan tanpa membuat thread baru. |
| HuggingFace Hub | Platform untuk berbagi dan download model ML. IndoBERT tersedia di sini. |
| VRAM | Video RAM — memori di GPU. RTX 4050 Laptop punya 6GB VRAM. |

---

*KarunaAI — Panduan v2.0 | 100% Free Stack | RTX 4050 Local*
