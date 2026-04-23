# KarunaAI Deployment Guide

Panduan lengkap untuk men-deploy KarunaAI sebagai REST API service agar developer dapat mengakses dan mengimplementasikan semua fitur (S1, S2, S3, S4, STT, TTS) ke dalam website mereka.

---

## 📋 Daftar Isi - Step-by-Step Guide

### PHASE 1: PERSIAPAN
1. [Arsitektur & Cara Kerja](#1-arsitektur-cara-kerja)
2. [Struktur Project](#2-struktur-project)
3. [Install Dependencies](#3-install-dependencies)

### PHASE 2: BUAT API
4. [Buat API Server (FastAPI)](#4-buat-api-server-fastapi)
5. [API Endpoints](#5-api-endpoints)
6. [Test API Lokal](#6-test-api-lokal)

### PHASE 3: DOCKERIZE
7. [Docker Basics](#7-docker-basics)
8. [Buat Dockerfile](#8-buat-dockerfile)
9. [Test Docker Lokal](#9-test-docker-lokal)

### PHASE 4: DEPLOY
10. [Deploy ke HuggingFace](#10-deploy-ke-huggingface)
11. [Deploy ke Render/Railway](#11-deploy-ke-renderrailway)
12. [Developer Access Guide](#12-developer-access-guide)

### EXTRA
13. [Troubleshooting](#13-troubleshooting)
14. [Security Checklist](#14-security-checklist)

---

# ============================================================
# PHASE 1: PERSIAPAN
# ============================================================

## 1. Arsitektur & Cara Kerja

### 1.1 Diagram Alur Deployment

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        DEVELOPER WEBSITE                                    │
│                   (Mengakses KarunaAI API)                                 │
│                                                                            │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│   │  /chat     │  │  /emotion  │  │  /crisis   │  │  /tts      │       │
│   │  endpoint  │  │  endpoint  │  │  endpoint  │  │  endpoint  │       │
│   └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘       │
└────────┼──────────────┼──────────────┼──────────────┼──────────────┼─────────────┘
         │              │              │              │              │
         ▼              ▼              ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        KARUNAAI API SERVER                                │
│                        (FastAPI + Uvicorn)                                │
│                                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐        │
│  │  KarunaOrchestrator                                          │        │
│  │  (Pipeline utama: S1 → S2 → S3 → S4)                  │        │
│  └─────────────────────────────────────────────────────────────────────┘        │
│                                                                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │   S1    │  │   S2    │  │   S3    │  │   S4    │                 │
│  │Convers. │  │Emotion  │  │ Crisis  │  │Summary  │                 │
│  │(Groq)   │  │(Local)  │  │(Local)  │  │(Groq)   │                 │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘                 │
│                                                                            │
│  ┌──────────┐  ┌──────────┐                                             │
│  │  STT    │  │  TTS    │                                             │
│  │(Eleven) │  │(Eleven) │                                             │
│  └──────────┘  └──────────┘                                             │
└────────┬─────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        EXTERNAL SERVICES                                   │
│  ┌──────────────┐  ┌──────────────────────┐                            │
│  │  Groq API    │  │  Eleven Labs API    │                            │
│  │  (LLM)      │  │  (STT + TTS)      │                            │
│  └──────────────┘  └──────────────────────┘                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Alur Request-Response

```
Developer Website                    KarunaAI API                  External Services
     │                                │                              │
     │  POST /chat                   │                              │
     │  { "message": "..." }        │                              │
     │ ───────────────────────────────►                              │
     │                                │                              │
     │                                │  S2: Emotion Engine      │
     │                                │ ──────────────────────► (Local Model)
     │                                │                              │
     │                                │  S3: Crisis Detection │
     │                                │ ──────────────────────► (Local Model)
     │                                │                              │
     │                                │  S1: Groq Chat     │
     │                                │ ──────────────────────► ─► Groq API
     │                                │                              │
     │  { "response": "...",         │                              │
     │    "emotion": {...},     │◄───────────────────────               │
     │    "crisis": {...} }     │                              │
     │ ◄────────────────────────│                              │
```

---

# ============================================================
# PHASE 2: BUAT API
# ============================================================

## 2. Struktur Project (dimana file-file disimpan)

```
karunaAI/
├── api/                          # REST API Server

---

## 3. Install Dependencies (library yang dibutuhkan)

### 3.1 Checklist Library

| Library | Fungsi | Sudah Ada? |
|---------|--------|---------|
| fastapi | API Server | ❌Perlu install|
| uvicorn | Run server | ❌Perlu install|
| pydantic | Validasi data | ❌Perlu install|
| groq | LLM S1 & S4 | ✅Sudah ada|
| torch | ML | ✅Sudah ada|
| transformers | ML | ✅Sudah ada|
| elevenlabs | Voice | ✅Sudah ada|
| sounddevice | Voice | ✅Sudah ada|

### 3.2 Install Command

```bash
# Install library yang belum ada (hanya baru saja)
pip install fastapi uvicorn[standard] pydantic pydantic-settings python-jose passlib httpx aiofiles

# ATAU jika ingin fresh install semua
pip install -r requirements.txt
pip install fastapi uvicorn[standard] pydantic pydantic-settings
```

### 3.3 Verify Install

```bash
# Check FastAPI
python -c "import fastapi; print(fastapi.__version__)"

# Check Uvicorn  
python -c "import uvicorn; print(uvicorn.__version__)"
```

---

# ============================================================
# PHASE 2: BUAT API (Lanjutan)
# ============================================================

## 4. Buat API Server (FastAPI) - Kode Lengkap

### 4.1 Main Application (api/main.py)

```python
# api/main.py - FastAPI application
```

karunaAI/
├── api/                          # REST API Server
│   ├── __init__.py
│   ├── main.py                    # FastAPI application
│   ├── endpoints/
│   │   ├── __init__.py
│   │   ├── chat.py                # /chat endpoint
│   │   ├── emotion.py             # /emotion endpoint
│   │   ├── crisis.py             # /crisis endpoint
│   │   ├── summary.py           # /summary endpoint
│   │   ├── tts.py              # /tts endpoint
│   │   └── stt.py              # /stt endpoint
│   ├── models/
│   │   ├── __init__.py
│   │   └── request_models.py     # Pydantic models
│   └── utils/
│       ├── __init__.py
│       ├── session_manager.py       # Manage user sessions
│       └── security.py        # API key validation
│
├── s1_conversational/              # S1: Conversational LLM
│   ├── prompt_builder.py
│   ├── groq_client.py
│   └── output_validator.py
│
├── s2_emotion/                 # S2: Emotion Detection
│   ├── emotion_engine.py
│   ├── data/
│   └── train_emotion.py
│
├── s3_crisis/                 # S3: Crisis Detection
│   ├── cds_engine.py
│   ├── cds_layer1.py
│   ├── cds_layer2.py
│   └── cds_layer3.py
│
├── s4_summary/                # S4: Summary Generator
│   └── summary_generator.py
│
├── voice/                    # Voice (STT/TTS)
│   ├── stt_engine.py
│   └── tts_engine.py
│
├── pipeline/                 # Orchestrator
│   └── orchestrator.py
│
├── models/                  # Trained models
│   ├── emotion_engine/
│   │   └── final/
│   │       ├── emotion_model.pt
│   │       ├── tokenizer.json
│   │       └── ...
│   └── crisis_detector/
│       └── final/
│           ├── crisis_model.pt
│           └── ...
│
├── docker/                     # Docker config
│   ├── Dockerfile
│   └── .dockerignore
│
├── requirements-api.txt          # API dependencies
├── render.yaml              # Render deployment config
├── .env.example           # Environment template
└── API.md                # Developer API docs
```

---

# ============================================================
# PHASE 2: BUAT API (Lanjutan)
# ============================================================

## 5. API Endpoints (Daftar semua fitur yang bisa diakses)

### 5.1 Daftar Semua Endpoint

| Method | Endpoint | Deskripsi | Input | Output |
|--------|---------|----------|-------|-------|-------|
| `POST` | `/chat` | Kirim pesan dan terima respons AI | `message`, `session_id` | `response`, `emotion`, `crisis` |
| `POST` | `/emotion` | Deteksi emosi dari teks | `text` | `dominant`, `score`, `distribution`, `topics`, `distress` |
| `POST` | `/crisis` | Deteksi level krisis | `text`, `emotion_history` | `level`, `score`, `triggers` |
| `POST` | `/session/start` | Mulai sesi baru | (kosong) | `session_id` |
| `POST` | `/session/end` | Akhiri sesi dan dapat ringkasan | `session_id` | `summary`, `flag` |
| `POST` | `/tts` | Konversi teks ke audio | `text`, `voice`, `mood` | `audio_base64` |
| `POST` | `/stt` | Konversi audio ke teks | `audio` (file/base64) | `text` |
| `GET` | `/voices` | List suara TTS tersedia | - | `voices` list |
| `GET` | `/health` | Health check | - | `status` |
| `GET` | `/models/info` | Info model yang loaded | - | `models` info |

### 3.2 Response Format

#### 3.2.1 /chat Response

```json
{
  "response": "Aku memahami perasaanmu...",
  "emotion": {
    "dominant": "sadness",
    "score": 0.82,
    "distribution": {
      "sadness": 0.82,
      "joy": 0.05,
      "anger": 0.08,
      "fear": 0.03,
      "neutral": 0.02
    },
    "topics": ["relationship"],
    "distress_score": 0.75
  },
  "crisis": {
    "level": "L1",
    "score": 0.28,
    "triggers": ["L1_keyword_L1"]
  },
  "session_id": "abc123-def456",
  "message_count": 3
}
```

#### 3.2.2 /emotion Response

```json
{
  "dominant": "sadness",
  "score": 0.82,
  "distribution": {
    "sadness": 0.82,
    "joy": 0.05,
    "anger": 0.08,
    "fear": 0.03,
    "neutral": 0.02
  },
  "topics": ["relationship"],
  "distress_score": 0.75
}
```

#### 3.2.3 /crisis Response

```json
{
  "level": "L2",
  "score": 0.65,
  "triggers": ["L2_model_crisis", "L3_trend_increasing"],
  "detail": {
    "l1_level": "NORMAL",
    "l2_label": "crisis",
    "l3_score": 0.15
  }
}
```

#### 3.2.4 /tts Response

```json
{
  "audio": "base64_encoded_audio...",
  "format": "mp3",
  "duration_seconds": 5.2
}
```

#### 3.2.5 /stt Response

```json
{
  "text": "Aku merasa sangat lelah akhir-akhir ini...",
  "language": "id",
  "confidence": 0.95
}
```

---

# ============================================================
# PHASE 2: BUAT API (Lanjutan - Kode Program)
# ============================================================

## 4. Buat API Server (FastAPI)

### 4.1 Dependencies

Buat file `requirements-api.txt`:

```txt
# Server
fastapi>=0.110.0
uvicorn[standard]>=0.27.0
python-multipart>=0.0.9
pydantic>=2.0.0
pydantic-settings>=2.0.0

# Existing dependencies
groq>=0.4.0
python-dotenv>=1.0.0
torch>=2.2.0
transformers>=4.40.0,<5.0.0
datasets>=2.19.0
sentencepiece>=0.2.0
scikit-learn>=1.4.0
accelerate>=0.30.0
numpy>=1.26.0
pandas>=2.2.0
protobuf==3.20.3

# Voice
elevenlabs>=1.50.0
sounddevice
scipy
soundfile

# Utilities
python-jose[cryptography]
passlib[bcrypt]
httpx
aiofiles
```

### 4.2 Main Application

Buat file `api/main.py`:

```python
# api/main.py
# KarunaAI REST API Server
# FastAPI application untuk melayani semua endpoint

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import endpoint routers
from api.endpoints import chat, emotion, crisis, summary, tts, stt, session, voices, models_info
from api.utils.security import verify_api_key

# ── API Key Security ─────────────────────────────────────────────────────────
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_api_key(request: Request, api_key: str = Depends(API_KEY_HEADER)):
    """Verify API key for protected endpoints."""
    # Skip verification if no API key configured (development mode)
    if not os.getenv("API_KEY_ENABLED") or os.getenv("API_KEY_ENABLED") == "false":
        return True
    
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    if not verify_api_key(api_key):
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    return True


# ── Lifespan Events ────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    logger.info("Starting KarunaAI API Server...")
    
    # Initialize models here (lazy loading)
    from s2_emotion.emotion_engine import EmotionEngine
    from s3_crisis.cds_engine import analyze_crisis
    
    # Store in app state
    app.state.emotion_engine = None
    app.state.crisis_analyzer = analyze_crisis
    
    logger.info("KarunaAI API Server started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down KarunaAI API Server...")


# ── Create FastAPI App ─────────────────────────────────────────────────
app = FastAPI(
    title="KarunaAI API",
    description="REST API untuk KarunaAI - AI Companion untuk Curhat Mental Health",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS Middleware ────────────────────────────────────────────────────────
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Include Routers ────────────────────────────────────────────────────────
app.include_router(
    chat.router,
    prefix="/api/v1",
    tags=["Chat"],
    dependencies=[Depends(get_api_key)],
)
app.include_router(
    emotion.router,
    prefix="/api/v1",
    tags=["Emotion"],
    dependencies=[Depends(get_api_key)],
)
app.include_router(
    crisis.router,
    prefix="/api/v1",
    tags=["Crisis"],
    dependencies=[Depends(get_api_key)],
)
app.include_router(
    summary.router,
    prefix="/api/v1",
    tags=["Summary"],
    dependencies=[Depends(get_api_key)],
)
app.include_router(
    tts.router,
    prefix="/api/v1",
    tags=["TTS"],
    dependencies=[Depends(get_api_key)],
)
app.include_router(
    stt.router,
    prefix="/api/v1",
    tags=["STT"],
    dependencies=[Depends(get_api_key)],
)
app.include_router(
    session.router,
    prefix="/api/v1",
    tags=["Session"],
    dependencies=[Depends(get_api_key)],
)
app.include_router(
    voices.router,
    prefix="/api/v1",
    tags=["Voices"],
)
app.include_router(
    models_info.router,
    prefix="/api/v1",
    tags=["Models"],
)


# ── Health Check ─────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health_check():
    """Check if API is running."""
    return {"status": "healthy", "service": "karunaai-api"}


# ── Rate Limiter (simple) ──────────────────────────────────────────────────
from collections import defaultdict
from datetime import datetime, timedelta

rate_limit_store = defaultdict(list)


@app.middleware("http")
async def rate_limiter(request: Request, call_next):
    """Simple rate limiting per IP."""
    if os.getenv("RATE_LIMIT_ENABLED") == "true":
        client_ip = request.client.host
        now = datetime.now()
        window = timedelta(minutes=1)
        limit = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
        
        # Clean old entries
        rate_limit_store[client_ip] = [
            t for t in rate_limit_store[client_ip] if t > now - window
        ]
        
        if len(rate_limit_store[client_ip]) >= limit:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"}
            )
        
        rate_limit_store[client_ip].append(now)
    
    response = await call_next(request)
    return response


# ── Error Handlers ────────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors."""
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": str(exc) if os.getenv("DEBUG") == "true" else "Something went wrong"
        }
    )
```

### 4.3 Chat Endpoint

Buat file `api/endpoints/chat.py`:

```python
# api/endpoints/chat.py
# Chat endpoint - Utama untuk percakapan dengan KarunaAI

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
import logging

from api.models.request_models import ChatRequest, ChatResponse
from pipeline.orchestrator import KarunaOrchestrator

logger = logging.getLogger(__name__)
router = APIRouter()

# Global session storage (in production, use Redis or database)
_sessions = {}


def get_or_create_orchestrator(session_id: Optional[str] = None) -> KarunaOrchestrator:
    """Get or create orchestrator for session."""
    from s2_emotion.emotion_engine import EmotionEngine
    
    if session_id and session_id in _sessions:
        return _sessions[session_id]
    
    # Lazy load emotion engine
    emotion_engine = EmotionEngine("models/emotion_engine/final")
    orchestrator = KarunaOrchestrator(emotion_engine)
    
    if session_id:
        _sessions[session_id] = orchestrator
    
    return orchestrator


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Kirim pesan dan terima respons dari KarunaAI.
    
    Ini adalah endpoint utama yang mengintegrasikan semua komponen:
    - S1: Generative AI response (Groq)
    - S2: Emotion detection
    - S3: Crisis detection
    - S4: Session summary (saat sesi diakhiri)
    
    Args:
        message: Pesan dari user
        session_id: ID sesi (opsional, akan dibuat baru jika kosong)
    
    Returns:
        ChatResponse dengan respons AI dan metadata
    """
    try:
        # Get or create session
        session_id = request.session_id or str(uuid.uuid4())
        
        # Get orchestrator
        orch = get_or_create_orchestrator(session_id)
        
        # Process message through pipeline
        result = orch.process(request.message)
        
        # Build response
        return ChatResponse(
            response=result.ai_response,
            emotion={
                "dominant": result.emotion_result.dominant,
                "score": result.emotion_result.score,
                "distribution": result.emotion_result.distribution,
                "topics": result.emotion_result.topics,
                "distress_score": result.emotion_result.distress_score
            },
            crisis={
                "level": result.cds_result.level,
                "score": result.cds_result.score,
                "triggers": result.cds_result.triggers
            },
            session_id=session_id,
            message_count=orch.msg_count,
            crisis_banner=result.crisis_banner
        )
    
    except Exception as e:
        logger.error(f"Error in /chat: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")


@router.post("/chat/validate")
async def validate_response(response: str, cds_level: str = "NORMAL"):
    """
    Validasi respons AI untuk memastikan kualitas.
    
    Args:
        response: Respons AI yang akan divalidasi
        cds_level: Level krisis saat ini (untuk menentukan strictness)
    
    Returns:
        Validasi result
    """
    from s1_conversational.output_validator import validate
    
    is_valid, reason = validate(response, cds_level=cds_level)
    
    return {
        "is_valid": is_valid,
        "reason": reason
    }
```

### 4.4 Emotion Endpoint

Buat file `api/endpoints/emotion.py`:

```python
# api/endpoints/emotion.py
# Emotion detection endpoint

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Lazy loaded engine
_emotion_engine = None


def get_emotion_engine():
    """Get or create emotion engine."""
    global _emotion_engine
    if _emotion_engine is None:
        from s2_emotion.emotion_engine import EmotionEngine
        _emotion_engine = EmotionEngine("models/emotion_engine/final")
    return _emotion_engine


class EmotionRequest(BaseModel):
    text: str
    return_topics: bool = True


class EmotionResponse(BaseModel):
    dominant: str
    score: float
    distribution: dict
    topics: Optional[list] = None
    distress_score: float


@router.post("/emotion", response_model=EmotionResponse)
async def analyze_emotion(request: EmotionRequest):
    """
    Deteksi emosi dari teks.
    
    Menggunakan S2: Emotion Engine (IndoBERT-based model)
    
    Args:
        text: Teks yang akan dianalisis
        return_topics: Include topik yang terdeteksi
    
    Returns:
        Emotion analysis result
    """
    try:
        engine = get_emotion_engine()
        result = engine.analyze(request.text)
        
        return EmotionResponse(
            dominant=result.dominant,
            score=result.score,
            distribution=result.distribution,
            topics=result.topics if request.return_topics else None,
            distress_score=result.distress_score
        )
    
    except Exception as e:
        logger.error(f"Error in /emotion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/emotion/labels")
async def get_emotion_labels():
    """Get list of emotion labels."""
    return {
        "emotions": ["joy", "sadness", "anger", "fear", "surprise", "disgust", "neutral"],
        "topics": ["work", "relationship", "family", "health", "finance", "self", "other"]
    }
```

### 4.5 Crisis Endpoint

Buat file `api/endpoints/crisis.py`:

```python
# api/endpoints/crisis.py
# Crisis detection endpoint

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class CrisisRequest(BaseModel):
    text: str
    emotion_history: Optional[List[dict]] = None


class CrisisResponse(BaseModel):
    level: str  # "NORMAL", "L1", "L2", "L3"
    score: float
    triggers: List[str]
    detail: Optional[dict] = None


@router.post("/crisis", response_model=CrisisResponse)
async def analyze_crisis(request: CrisisRequest):
    """
    Deteksi level krisis dari teks dan riwayat emosi.
    
    Menggunakan S3: Crisis Detection System (3-layer)
    - Layer 1: Keyword/Regex detection
    - Layer 2: IndoBERT model
    - Layer 3: History trend analysis
    
    Args:
        text: Teks yang akan dianalisis
        emotion_history: Riwayat emosi (opsional, untuk Layer 3)
    
    Returns:
        Crisis analysis result dengan level dan skor
    """
    try:
        from pipeline.orchestrator import KarunaOrchestrator
        from s3_crisis.cds_engine import analyze_crisis
        
        # Convert emotion_history if provided
        emotion_objs = []
        if request.emotion_history:
            from dataclasses import dataclass
            @dataclass
            class EmotionObj:
                distress_score: float
            emotion_objs = [
                EmotionObj(e.get("distress_score", 0.0)) 
                for e in request.emotion_history
            ]
        
        result = analyze_crisis(request.text, emotion_objs)
        
        return CrisisResponse(
            level=result.level,
            score=result.score,
            triggers=result.triggers,
            detail=result.detail
        )
    
    except Exception as e:
        logger.error(f"Error in /crisis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/crisis/levels")
async def get_crisis_levels():
    """Get explanation of crisis levels."""
    return {
        "levels": {
            "NORMAL": {
                "description": "Tidak ada sinyal krisis terdeteksi",
                "action": "Lanjutkan percakapan normal"
            },
            "L1": {
                "description": "Sedikit tanda-tanda distress",
                "action": "Perhatikan dan tunjukkan empati"
            },
            "L2": {
                "description": "Tanda-tanda krisis yang nyata",
                "action": "Berikan dukungan lebih, pertimbangkan referal"
            },
            "L3": {
                "description": "Krisis serius - risiko tinggi",
                "action": "Segera berikan nomor bantuan krisis (119 ext 8)"
            }
        }
    }
```

### 4.6 TTS Endpoint

Buat file `api/endpoints/tts.py`:

```python
# api/endpoints/tts.py
# Text-to-Speech endpoint

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional
import base64
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Valid voices
VALID_VOICES = ["sarah", "charlotte", "aria", "roger", "jessica", "brian", "honeypie"]
VALID_MOODS = ["calm", "warm", "gentle", "concerned"]


class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = "sarah"
    mood: Optional[str] = None
    speed: Optional[float] = 1.0
    stability: Optional[float] = None
    similarity_boost: Optional[float] = None


class TTSResponse(BaseModel):
    audio: str  # base64 encoded
    format: str
    duration_seconds: Optional[float] = None


@router.post("/tts", response_model=TTSResponse)
async def text_to_speech(request: TTSRequest):
    """
    Konversi teks ke audio menggunakan Eleven Labs TTS.
    
    Menghasilkan audio berkualitas tinggi dengan suara natural
    yang support bahasa Indonesia.
    
    Args:
        text: Teks yang akan dikonversi ke audio
        voice: Nama suara yang digunakan (default: "sarah")
        mood: Mood preset ("calm", "warm", "gentle", "concerned")
        speed: Kecepatan bicara (0.5 - 2.0, default: 1.0)
        stability: Stabilitas suara (0.0 - 1.0)
        similarity_boost: Similarity ke suara asli (0.0 - 1.0)
    
    Returns:
        Audio dalam format base64
    """
    try:
        from voice.tts_engine import TTSEngine, apply_mood
        
        # Validate voice
        if request.voice and request.voice not in VALID_VOICES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid voice. Valid: {VALID_VOICES}"
            )
        
        # Create engine
        engine = TTSEngine()
        
        # Apply voice
        if request.voice:
            engine.set_voice_by_name(request.voice)
        
        # Apply mood if specified
        if request.mood:
            if request.mood not in VALID_MOODS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid mood. Valid: {VALID_MOODS}"
                )
            apply_mood(engine, request.mood)
        
        # Apply custom parameters
        if request.speed:
            engine.set_speed(request.speed)
        if request.stability is not None:
            engine.set_stability(request.stability)
        if request.similarity_boost is not None:
            engine.set_similarity_boost(request.similarity_boost)
        
        # Generate audio
        audio_bytes = engine.synthesize(request.text)
        
        # Encode to base64
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        
        return TTSResponse(
            audio=audio_b64,
            format="mp3"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in /tts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tts/file")
async def text_to_speech_file(
    text: str,
    voice: str = "sarah",
    mood: str = None
):
    """
    Konversi teks ke file audio (returns file path).
    
    Berguna untuk debugging atau jika client prefer menerima file.
    
    Args:
        text: Teks untuk dikonversi
        voice: Nama suara
        mood: Mood preset
    
    Returns:
        Path ke file audio
    """
    from voice.tts_engine import TTSEngine, apply_mood
    import tempfile
    import os
    
    engine = TTSEngine()
    engine.set_voice_by_name(voice)
    
    if mood:
        apply_mood(engine, mood)
    
    # Save to temp file
    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    tmp.close()
    
    try:
        engine.save(text, tmp.name)
        
        with open(tmp.name, "rb") as f:
            audio_data = f.read()
        
        os.unlink(tmp.name)
        
        return Response(
            content=audio_data,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": f"attachment; filename=karuna_response.mp3"
            }
        )
    
    except Exception as e:
        logger.error(f"Error in /tts/file: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

### 4.7 STT Endpoint

Buat file `api/endpoints/stt.py`:

```python
# api/endpoints/stt.py
# Speech-to-Text endpoint

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional
import base64
import io
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class STTRequest(BaseModel):
    audio: str  # base64 encoded audio
    language: Optional[str] = "id"


class STTResponse(BaseModel):
    text: str
    language: str
    confidence: Optional[float] = None


@router.post("/stt", response_model=STTResponse)
async def speech_to_text(request: STTRequest):
    """
    Konversi audio ke teks menggunakan Eleven Labs STT.
    
    Menggunakan model Whisper yang支持 bahasa Indonesia dengan akurat.
    
    Args:
        audio: Audio dalam format base64 (WAV, MP3, dll)
        language: Kode bahasa (default: "id" untuk Indonesia)
    
    Returns:
        Teks hasil transkripsi
    """
    try:
        from voice.stt_engine import transcribe_audio
        
        # Decode base64
        audio_bytes = base64.b64decode(request.audio)
        
        # Transcribe
        text = transcribe_audio(audio_bytes, language=request.language or "id")
        
        if not text:
            raise HTTPException(
                status_code=400,
                detail="Could not transcribe audio"
            )
        
        return STTResponse(
            text=text,
            language=request.language or "id"
        )
    
    except Exception as e:
        logger.error(f"Error in /stt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stt/file")
async def speech_to_text_file(
    audio: UploadFile = File(...),
    language: str = "id"
):
    """
    Konversi file audio ke teks.
    
    Upload file audio langsung (bukan base64).
    
    Args:
        audio: File audio (WAV, MP3, dll)
        language: Kode bahasa
    
    Returns:
        Teks hasil transkripsi
    """
    try:
        from voice.stt_engine import transcribe_file
        
        # Read uploaded file
        audio_bytes = await audio.read()
        
        # Save to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(
            suffix=".wav", 
            delete=False
        ) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        
        try:
            # Transcribe
            text = transcribe_file(tmp_path, language)
        finally:
            import os
            os.unlink(tmp_path)
        
        if not text:
            raise HTTPException(
                status_code=400,
                detail="Could not transcribe audio"
            )
        
        return {"text": text, "language": language}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in /stt/file: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

### 4.8 Session Endpoint

Buat file `api/endpoints/session.py`:

```python
# api/endpoints/session.py
# Session management endpoints

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Session storage (in production, use database)
_sessions = {}


class StartSessionResponse(BaseModel):
    session_id: str
    message: str


class EndSessionRequest(BaseModel):
    session_id: str


class EndSessionResponse(BaseModel):
    session_id: str
    summary: str
    flag: str
    flag_reasoning: str
    emotion_timeline: list
    cds_level: str


@router.post("/session/start", response_model=StartSessionResponse)
async def start_session():
    """
    Mulai sesi baru dengan KarunaAI.
    
    Returns:
        Session ID yang dapat digunakan untuk percakapan
    """
    session_id = str(uuid.uuid4())
    
    # Initialize orchestrator
    from s2_emotion.emotion_engine import EmotionEngine
    from pipeline.orchestrator import KarunaOrchestrator
    
    emotion_engine = EmotionEngine("models/emotion_engine/final")
    orchestrator = KarunaOrchestrator(emotion_engine)
    
    _sessions[session_id] = orchestrator
    
    return StartSessionResponse(
        session_id=session_id,
        message="Sesi baru dimulai. Karuna siap mendengarkan."
    )


@router.post("/session/end", response_model=EndSessionResponse)
async def end_session(request: EndSessionRequest):
    """
    Akhiri sesi dan dapat ringkasan.
    
    Args:
        session_id: ID sesi yang akan diakhiri
    
    Returns:
        Ringkasan sesi untuk psikolog
    """
    if request.session_id not in _sessions:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )
    
    orch = _sessions[request.session_id]
    
    # End session
    summary = orch.end_session()
    
    if summary is None:
        raise HTTPException(
            status_code=400,
            detail="No messages in session"
        )
    
    # Remove from storage
    del _sessions[request.session_id]
    
    return EndSessionResponse(
        session_id=request.session_id,
        summary=summary.paragraf,
        flag=summary.flag,
        flag_reasoning=summary.flag_reasoning,
        emotion_timeline=[
            {
                "dominant": e.dominant,
                "distress": e.distress_score
            }
            for e in orch.emotion_history
        ],
        cds_level=summary.cds_level_akhir
    )


@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get current session state."""
    if session_id not in _sessions:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )
    
    orch = _sessions[session_id]
    
    return {
        "session_id": session_id,
        "message_count": orch.msg_count,
        "emotion_history": [
            {
                "dominant": e.dominant,
                "distress": e.distress_score
            }
            for e in orch.emotion_history
        ],
        "last_cds": {
            "level": orch.last_cds_result.level,
            "score": orch.last_cds_result.score
        } if orch.last_cds_result else None
    }
```

### 4.9Voices Endpoint

Buat file `api/endpoints/voices.py`:

```python
# api/endpoints/voices.py
# Voices listing endpoint

from fastapi import APIRouter
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/voices")
async def list_voices():
    """
    Get list of available TTS voices.
    
    Returns:
        Dictionary of available voices dengan deskripsi
    """
    from voice.tts_engine import AVAILABLE_VOICES, MOOD_PRESETS
    
    return {
        "voices": {
            name: {
                "voice_id": voice_id,
                "description": _get_voice_description(name)
            }
            for name, voice_id in AVAILABLE_VOICES.items()
        },
        "moods": MOOD_PRESETS
    }


def _get_voice_description(name: str) -> str:
    """Get description for voice."""
    descriptions = {
        "sarah": "Female, warm dan friendly - cocok untuk percakapan sehari-hari",
        "charlotte": "Female, calm dan professional",
        "aria": "Female, expressive dan animated",
        "roger": "Male, professional dan clear",
        "jessica": "Female, conversational",
        "brian": "Male, deepVoice",
        "honeypie": "Female, sweet dan warm"
    }
    return descriptions.get(name, "Unknown voice")


@router.get("/voices/{voice_name}/preview")
async def voice_preview(voice_name: str, text: str = "Halo, aku Karuna."):
    """
    Get audio preview untuk voice tertentu.
    
    Args:
        voice_name: Nama voice
        text: Teks untuk preview
    
    Returns:
        Audio dalam format base64
    """
    import base64
    from voice.tts_engine import TTSEngine
    
    if voice_name not in ["sarah", "charlotte", "aria", "roger", "jessica", "brian", "honeypie"]:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Voice not found")
    
    engine = TTSEngine()
    engine.set_voice_by_name(voice_name)
    
    audio_bytes = engine.synthesize(text)
    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
    
    return {
        "audio": audio_b64,
        "format": "mp3"
    }
```

### 4.10 Models Info Endpoint

Buat file `api/endpoints/models_info.py`:

```python
# api/endpoints/models_info.py
# Model information endpoint

from fastapi import APIRouter
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/models/info")
async def get_models_info():
    """
    Get information tentang loaded models.
    
    Returns:
        Info tentang model S2 (Emotion) dan S3 (Crisis)
    """
    import torch
    
    return {
        "models": {
            "emotion_engine": {
                "name": "IndoBERT-based Emotion Classifier",
                "path": "models/emotion_engine/final",
                "device": "cuda" if torch.cuda.is_available() else "cpu",
                "classes": ["joy", "sadness", "anger", "fear", "surprise", "disgust", "neutral"]
            },
            "crisis_detector": {
                "name": "Crisis Detection System (3-layer)",
                "path": "models/crisis_detector/final",
                "layers": {
                    "layer1": "Keyword/Regex",
                    "layer2": "IndoBERT classifier",
                    "layer3": "History trend analysis"
                },
                "levels": ["NORMAL", "L1", "L2", "L3"]
            }
        },
        "llm": {
            "provider": "Groq",
            "model": "llama-3.3-70b-versatile"
        },
        "voice": {
            "stt": "Eleven Labs Scribe",
            "tts": "Eleven Labs Multilingual v3"
        }
    }


@router.get("/models/loaded")
async def get_loaded_models():
    """Check which models are currently loaded."""
    return {
        "status": "ready",
        "loaded": [
            "emotion_engine",
            "crisis_detector_base"
        ]
    }
```

### 4.11 Request/Response Models

Buat file `api/models/request_models.py`:

```python
# api/models/request_models.py
# Pydantic models untuk request dan response

from pydantic import BaseModel, Field
from typing import Optional, List, Dict


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000)
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    emotion: Dict
    crisis: Dict
    session_id: str
    message_count: int
    crisis_banner: str = ""


class EmotionRequest(BaseModel):
    text: str = Field(..., min_length=1)
    return_topics: bool = True


class EmotionResponse(BaseModel):
    dominant: str
    score: float
    distribution: Dict
    topics: Optional[List[str]] = None
    distress_score: float


class CrisisRequest(BaseModel):
    text: str = Field(..., min_length=1)
    emotion_history: Optional[List[Dict]] = None


class CrisisResponse(BaseModel):
    level: str
    score: float
    triggers: List[str]
    detail: Optional[Dict] = None


class SummaryResponse(BaseModel):
    session_id: str
    summary: str
    flag: str
    flag_reasoning: str
    tren_distress: str
    jumlah_pesan: int


class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    voice: str = "sarah"
    mood: Optional[str] = None
    speed: float = Field(default=1.0, ge=0.5, le=2.0)


class TTSResponse(BaseModel):
    audio: str  # base64
    format: str


class STTRequest(BaseModel):
    audio: str  # base64
    language: str = "id"


class STTResponse(BaseModel):
    text: str
    language: str
    confidence: Optional[float] = None


class ErrorResponse(BaseModel):
    detail: str
    code: Optional[str] = None
```

### 4.12 Security Utilities

Buat file `api/utils/security.py`:

```python
# api/utils/security.py
# Security utilities untuk API key validation

import os
import hashlib
from typing import Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Simple API key store (in production, use database)
# Format: {"api_key_hash": {"name": "...", "created": ..., "rate_limit": ...}}
_api_keys = {}

# Initialize keys from environment
def _init_api_keys():
    """Initialize API keys from environment."""
    keys_env = os.getenv("API_KEYS", "")
    if keys_env:
        for i, key in enumerate(keys_env.split(",")):
            key = key.strip()
            if key:
                key_hash = hashlib.sha256(key.encode()).hexdigest()
                _api_keys[key_hash] = {
                    "name": f"key_{i+1}",
                    "created": datetime.now(),
                    "rate_limit": int(os.getenv("RATE_LIMIT_PER_KEY", "1000"))
                }

_init_api_keys()


def verify_api_key(api_key: str) -> bool:
    """
    Verify API key.
    
    Args:
        api_key: API key to verify
    
    Returns:
        True if valid, False otherwise
    """
    if not api_key:
        return False
    
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    return key_hash in _api_keys


def get_api_key_info(api_key: str) -> Optional[dict]:
    """Get info about API key."""
    if not api_key:
        return None
    
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    return _api_keys.get(key_hash)


def generate_api_key(name: str = "default") -> str:
    """
    Generate new API key.
    
    Args:
        name: Name for the key
    
    Returns:
        New API key
    """
    import secrets
    
    key = f"ka_{secrets.token_urlsafe(32)}"
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    
    _api_keys[key_hash] = {
        "name": name,
        "created": datetime.now(),
        "rate_limit": int(os.getenv("RATE_LIMIT_PER_KEY", "1000"))
    }
    
    return key


def revoke_api_key(api_key: str) -> bool:
    """
    Revoke API key.
    
    Args:
        api_key: Key to revoke
    
    Returns:
        True if revoked, False if not found
    """
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    
    if key_hash in _api_keys:
        del _api_keys[key_hash]
        return True
    
    return False


# ── Input Validation ───────────────────────────────────────────────────
def validate_text_input(text: str, max_length: int = 10000) -> bool:
    """
    Validate text input for safety.
    
    Args:
        text: Text to validate
        max_length: Maximum allowed length
    
    Returns:
        True if valid
    """
    if not text or len(text) > max_length:
        return False
    
    # Check for null bytes
    if "\x00" in text:
        return False
    
    return True


def sanitize_input(text: str) -> str:
    """
    Sanitize text input.
    
    Args:
        text: Text to sanitize
    
    Returns:
        Sanitized text
    """
    # Remove null bytes
    text = text.replace("\x00", "")
    
    # Strip whitespace
    text = text.strip()
    
    return text
```

### 4.13 Session Manager

Buat file `api/utils/session_manager.py`:

```python
# api/utils/session_manager.py
# Session management utilities

import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class Session:
    """Session object."""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.created_at = datetime.now()
        self.last_active = datetime.now()
        self.message_count = 0
        self.metadata: Dict = {}


class SessionManager:
    """
    Manages user sessions.
    
    In production, replace with Redis or database.
    """
    
    def __init__(self, session_timeout_minutes: int = 60):
        self.sessions: Dict[str, Session] = {}
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
    
    def create_session(self) -> str:
        """Create new session."""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = Session(session_id)
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID."""
        session = self.sessions.get(session_id)
        
        if session is None:
            return None
        
        # Check timeout
        if datetime.now() - session.last_active > self.session_timeout:
            self.delete_session(session_id)
            return None
        
        return session
    
    def update_session(self, session_id: str):
        """Update session last active time."""
        if session_id in self.sessions:
            self.sessions[session_id].last_active = datetime.now()
            self.sessions[session_id].message_count += 1
    
    def delete_session(self, session_id: str):
        """Delete session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def cleanup_expired(self):
        """Remove expired sessions."""
        now = datetime.now()
        expired = [
            sid for sid, session in self.sessions.items()
            if now - session.last_active > self.session_timeout
        ]
        
        for sid in expired:
            del self.sessions[sid]
        
        return len(expired)


# Global instance
_session_manager = SessionManager()


def get_session_manager() -> SessionManager:
    """Get global session manager."""
    return _session_manager
```

---

# ============================================================
# PHASE 3: DOCKERIZE
# ============================================================

# ============================================================
# PHASE 3: DOCKERIZE
# ============================================================

## 7. Docker Basics (Apa itu Docker & kenapa perlu)

### 7.1 Apa itu Docker? (Penjelasan untuk Pemula)

**Docker** adalah tool yang membuat aplikasi bisa jalan di mana saja, sama seperti di laptop kamu.

| Tanpa Docker | Dengan Docker |
|-------------|----------------|
| Install Python, pip, dll manually | Semua sudah included |
| Bisa error karena environment berbeda | Sama persis di semua tempat |
| Susah deploy ke server | Mudah deploy |
| Bingung troubleshooting | Konsisten |

### 7.2 Istilah Penting Docker

| Istilah | Arti |
|--------|------|
| Image | Template/blueprint aplikasi |
| Container | Aplikasi yang berjalan dari image |
| Dockerfile | File instruksi buat build image |
| Docker Hub | Repository untuk Docker images |

### 7.3 Install Docker

### 7.1 Apa itu Dockerfile? (Penjelasan Singkat)

Dockerfile adalah file konfigurasi yang tells Docker how to build image. Dengan Dockerfile:
- Aplikasi bisa dijalankan di mana saja (laptop, server, cloud)
- Tidak perlu install dependencies manual
- Consistent environment

### 7.2 Buat Dockerfile

Buat file `docker/Dockerfile`:

```dockerfile
# KarunaAI API Server Dockerfile
# Multi-stage build untuk production

# Stage 1: Base
FROM python:3.10-slim as base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt


# Stage 2: Application
FROM base as app

# Copy application code
COPY . .

# Create models directory (bind mount in production)
RUN mkdir -p models/emotion_engine/final models/crisis_detector/final


# Stage 3: Production
FROM base as production

# Add non-root user
RUN useradd -m -u 1000 appuser
USER appuser

WORKDIR /app

COPY --from=app /app .


# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 5.2 Docker Compose

Buat file `docker/docker-compose.yml`:

```yaml
version: '3.8'

services:
  karuna-api:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    ports:
      - "8000:8000"
    env_file:
      - ../.env
    volumes:
      - ../models:/app/models:ro
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  # Optional: Redis for session storage
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    restart: unless-stopped

volumes:
  redis-data:
```

### 5.3 .dockerignore

Buat file `docker/.dockerignore`:

```
# Git
.git
.gitignore

# Python
__pycache__
*.py[cod]
*$py.class
*.so
.Python
.env
.venv
env/
venv/
ENV/
.pytest_cache/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Documentation
*.md
!README.md

# Data (keep models)
data/
s2_emotion/data/
s3_crisis/data/
!models/emotion_engine/final/*
!models/crisis_detector/final/*

# Demo
demo/
*.pyc

# Logs
*.log

# OS
.DS_Store
Thumbs.db
```

---

# ============================================================
# PHASE 4: DEPLOY
# ============================================================

## 8. Environment Variables (API Keys & Secrets)

### 6.1 Environment Template

Buat file `.env.example`:

```bash
# =====================================================
# KarunaAI API - Environment Variables
# =====================================================
# Copy this file to .env and fill in the values

# =====================================================
# API Configuration
# =====================================================
# Enable API key authentication
API_KEY_ENABLED=true

# API keys (comma separated, for multiple keys)
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
API_KEYS=your_api_key_here

# Rate limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_KEY=1000

# CORS - comma separated origins
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Debug mode (set to false in production)
DEBUG=false


# =====================================================
# Groq API (S1 & S4)
# =====================================================
# Get from https://console.groq.com/
GROQ_API_KEY=your_groq_api_key


# =====================================================
# Eleven Labs API (STT & TTS)
# =====================================================
# Get from https://elevenlabs.io/
ELEVENLABS_API_KEY=your_elevenlabs_api_key


# =====================================================
# Model Paths (don't change these)
# =====================================================
EMOTION_MODEL_PATH=models/emotion_engine/final
CRISIS_MODEL_PATH=models/crisis_detector/final


# =====================================================
# Session Configuration
# =====================================================
# Session timeout in minutes
SESSION_TIMEOUT=60

# Maximum messages per session
MAX_MESSAGES_PER_SESSION=100
```

### 6.2 Required Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | Yes | API key untuk Groq (S1 & S4) |
| `ELEVENLABS_API_KEY` | Yes (if using voice) | API key untuk Eleven Labs |
| `API_KEYS` | No | List API keys for developer access |
| `API_KEY_ENABLED` | No | Enable/disable API key (default: disabled) |

---

## 9. Deploy ke PaaS (HuggingFace, Render, Railway)

### 9.1 Render.com (Recommended)

Render adalah platform PaaS yang推荐 karena:

- ✅ Easy Python deployment
- ✅ Free tier tersedia (250 hours/month)
- ✅ Auto-deploy from GitHub
- ✅ Environment variables management
- ✅ Health checks support

#### 9.1.1 Langkah Deployment ke Render

1. **Push code ke GitHub**

```bash
git init
git add .
git commit -m "Initial commit: KarunaAI API"
git branch -M main
git remote add origin https://github.com/yourusername/karunaAI.git
git push -u origin main
```

2. **Buat Render Account**

- Kunjungi https://render.com
- Sign up dengan GitHub

3. **Create Web Service**

- Dashboard → New → Web Service
- Connect GitHub repository
- Konfigurasi:

```
Name: karuna-api
Environment: Python
Build Command: pip install -r requirements-api.txt
Start Command: uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

4. **Set Environment Variables**

- Advanced → Environment Variables
- Tambahkan:
  - `GROQ_API_KEY`: your_groq_api_key
  - `ELEVENLABS_API_KEY`: your_elevenlabs_api_key
  - `API_KEY_ENABLED`: false (atau true jika pakai API key)

5. **Deploy**

- Klik "Create Web Service"
- Tunggu build & deploy (~5-10 menit)

#### 9.1.2 render.yaml (Alternative)

Buat file `render.yaml` di root:

```yaml
services:
  - type: web
    name: karuna-api
    env: python
    buildCommand: pip install -r requirements-api.txt
    startCommand: uvicorn api.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: GROQ_API_KEY
        sync: false
      - key: ELEVENLABS_API_KEY
        sync: false
      - key: API_KEY_ENABLED
        value: "false"
        sync: false
    autoDeploy: true
    plan: free
```

### 7.2 Railway

#### 9.2 Railway

1. **Install Railway CLI**

```bash
npm install -g @railway/cli
railway login
```

2. **Initialize Project**

```bash
railway init
railway add
```

3. **Set Variables**

```bash
railway env set GROQ_API_KEY=your_key
railway env set ELEVENLABS_API_KEY=your_key
```

4. **Deploy**

```bash
railway up
```

### 9.3 HuggingFace Spaces ( comprehensive)

HuggingFace adalah platform yang sangat cocok untuk deploy ML models karena:
- ✅ Free tier dengan GPU (untuk model inference)
- ✅ Built-in model hosting
- ✅ Spaces untuk API server
- ✅ Easy sharing dengan community
- ✅ Version control untuk models

Ada 2 cara deploy di HuggingFace:

---

#### 9.3.1 Cara 1: Deploy Models Saja (tanpa API server)

Ini cocok kalau kamu mau share model saja, dan developer akan download sendiri.

##### Step 1: Siapkan Model untuk Upload

```bash
# Install HuggingFace Hub
pip install huggingface_hub
```

##### Step 2: Upload Emotion Model

```python
# python: upload_emotion_model.py
from huggingface_hub import HfApi, create_repo

api = HfApi()

# Login first (akan meminta token)
# Dapatkan token dari https://huggingface.co/settings/tokens
api.login("your_huggingface_token")

# Create repository
repo_id = "yourusername/karuna-emotion"
create_repo(repo_id, repo_type="model", exist_ok=True)

# Upload files
api.upload_folder(
    folder_path="models/emotion_engine/final",
    repo_id=repo_id,
    repo_type="model",
)
```

Atau dengan CLI:

```bash
# Login
huggingface-cli login

# Create repo
huggingface-cli repo create karuna-emotion --type model

# Upload
huggingface-cli upload karuna-emotion models/emotion_engine/final
```

##### Step 3: Upload Crisis Model

```bash
huggingface-cli repo create karuna-crisis --type model
huggingface-cli upload karuna-crisis models/crisis_detector/final
```

##### Step 4: Verify Upload

```bash
# Check di browser:
# https://huggingface.co/yourusername/karuna-emotion

# Atau via CLI:
huggingface-cli ls karuna-emotion
```

##### Cara Developer Menggunakan Model yang Diupload

```python
# Developer bisa load model langsung dari HuggingFace
from transformers import AutoModel, AutoTokenizer

# Load emotion model
emotion_model = AutoModel.from_pretrained("yourusername/karuna-emotion")
emotion_tokenizer = AutoTokenizer.from_pretrained("yourusername/karuna-emotion")

# Load crisis model  
crisis_model = AutoModel.from_pretrained("yourusername/karuna-crisis")
crisis_tokenizer = AutoTokenizer.from_pretrained("yourusername/karuna-crisis")

# Inference
inputs = emotion_tokenizer("Aku merasa sedih", return_tensors="pt")
outputs = emotion_model(**inputs)
```

---

#### 9.3.2 Cara 2: Deploy API Server (Full API Access)

Ini yang developer butuhkan - API endpoint lengkap yang bisa langsung di-consume.

##### Prerequisite: Persiapan File

Sebelum deploy, buat struktur file yang tepat untuk HuggingFace Spaces:

```
karuna-api/
├── app.py                    # FastAPI/Gradio app (WAJIB)
├── requirements.txt          # Dependencies
├── models/                   # Local models (akan di-gitignore di Spaces)
│   ├── emotion_engine/final/
│   └── crisis_detector/final/
├── api/                     # API code (bisa di-separate)
│   ├── __init__.py
│   ├── main.py
│   └── endpoints/
│       ├── __init__.py
│       ├── chat.py
│       ├── emotion.py
│       ├── crisis.py
│       ├── tts.py
│       └── stt.py
├── s1_conversational/       # Link atau copy dari project
├── s2_emotion/
├── s3_crisis/
├── s4_summary/
├── voice/
├── pipeline/
└── .env                    # Jangan di-commit! Gunakan Secrets
```

##### Option A: Deploy dengan Docker (Recommended - Langkah Lengkap)

HuggingFace Spaces mendukung Docker - jadi kita bisa deploy FastAPI seperti di lokal.

**KENAPA DOCKER?**
- ✅ Same environment seperti lokal
- ✅ Semua dependencies included
- ✅ Bisa pakai GPU di HuggingFace
- ✅ Reliable & reproducible

**Step 1: Prerequisites - Install Docker dulu**

```bash
# Windows: Download dari https://docker.com/products/docker-desktop
# Mac: Download dari https://docker.com/products/docker-desktop
# Linux:
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

**Verify Installation:**
```bash
docker --version
docker-compose --version
```

**Step 2: Siapkan app.py untuk Spaces**

Buat `app.py` untuk HuggingFace Spaces:

```python
# app.py
# KarunaAI API untuk HuggingFace Spaces
# Menggunakan FastAPI dengan Gradio client

import os
import gradio as gr
from fastapi import FastAPI
from fastapi.staticfiles import Static
from api.main import app as fastapi_app

# Override host untuk produksi
os.environ["API_KEY_ENABLED"] = os.getenv("API_KEY_ENABLED", "false")

# Serve API at /api route
app = FastAPI()
app.mount("/api", fastapi_app)

# Gradio health check UI
@app.get("/")
def read_root():
    return {"message": "KarunaAI API Running", "docs": "/api/docs"}

# Gradio UI for demo (optional)
# Ini akan muncul di halaman Space
demo = gr.Interface(
    fn=lambda x: x,  # Simple echo for testing
    inputs="textbox",
    outputs="textbox",
    title="KarunaAI Test"
)

# Mount Gradio
gr.mount_gradio_app(app, demo, "/")
```

**Step 2: Setup requirements.txt**

```txt
# requirements.txt untuk HuggingFace Spaces
fastapi>=0.110.0
uvicorn[standard]>=0.27.0
pydantic>=2.0.0

# ML dependencies
torch>=2.2.0
transformers>=4.40.0,<5.0.0
scikit-learn>=1.4.0

# API
groq>=0.4.0
python-dotenv>=1.0.0

# Voice
elevenlabs>=1.50.0
sounddevice
scipy

# Gradio
gradio>=4.0.0
httpx
```

**Step 3: Push ke GitHub**

```bash
# Initialize git
git init
git add .
git commit -m "KarunaAI API for HuggingFace Spaces"

# Create GitHub repo di https://github.com/new
git remote add origin https://github.com/yourusername/karuna-api.git
git push -u origin main
```

**Step 4: Create Space**

1. Buka https://huggingface.co/new-space
2. Pilih konfigurasi:

| Setting | Value |
|---------|-------|
| Space SDK | **Docker** |
| Hardware | CPU atau GPU (free) |
| Repository Name | karuna-ai |
| License | MIT |

3. Select "Link to GitHub repo"

**Step 5: Set Secrets/Variables**

Di Space settings, tambahkan:

```
Key: GROQ_API_KEY
Value: your_groq_api_key

Key: ELEVENLABS_API_KEY  
Value: your_elevenlabs_api_key
```

**Step 6: Deploy**

- Klik "Create Space"
- Tunggu build (5-10 menit)
- API akan available di: `https://yourusername-karuna-ai.hf.space/api/v1`

---

##### Option B: Deploy tanpa Docker (Simpler)

 Kalau tidak mau pakai Docker, bisa langsung:

**Step 1: Create Space dengan Gradio SDK**

1. https://huggingface.co/new-space
2. Pilih: **Space SDK: Gradio**
3. Hardware: CPU

**Step 2: Buat app.py**

```python
# app.py - Gradio version
# Simplified API untuk HuggingFace Spaces

import gradio as gr
import os
from dotenv import load_dotenv

load_dotenv()

# Import existing modules
from s1_conversational.groq_client import chat_with_groq
from s2_emotion.emotion_engine import EmotionEngine
from s3_crisis.cds_engine import analyze_crisis

# Load model (lazy loading)
emotion_engine = None

def get_emotion_engine():
    global emotion_engine
    if emotion_engine is None:
        emotion_engine = EmotionEngine("models/emotion_engine/final")
    return emotion_engine

# ── API Functions ───────────────────────────────────────────────

def chat(message, session_state=None):
    """Chat endpoint"""
    # Quick mock response untuk demo
    # Full implementation: use orchestrator
    return {
        "response": f"Karuna mendengar: {message}",
        "emotion": {"dominant": "neutral", "score": 0.5},
        "session_state": session_state
    }

def emotion(text):
    """Emotion detection"""
    engine = get_emotion_engine()
    result = engine.analyze(text)
    return {
        "dominant": result.dominant,
        "score": result.score,
        "distribution": result.distribution,
        "distress_score": result.distress_score
    }

def crisis(text):
    """Crisis detection"""
    result = analyze_crisis(text, [])
    return {
        "level": result.level,
        "score": result.score,
        "triggers": result.triggers
    }

# ── Gradio Interface ──────────────────────────────────────

with gr.Blocks(title="KarunaAI") as demo:
    gr.Markdown("# KarunaAI API")
    gr.Markdown("API untuk fitur curhat dengan AI")
    
    with gr.Tab("Chat"):
        chat_input = gr.Textbox(label="Pesan")
        chat_output = gr.Textbox(label="Respons")
        chat_btn = gr.Button("Kirim")
        chat_btn.click(chat, inputs=chat_input, outputs=chat_output)
    
    with gr.Tab("Emotion"):
        emo_input = gr.Textbox(label="Teks")
        emo_output = gr.JSON(label="Hasil Emosi")
        emo_btn = gr.Button("Deteksi")
        emo_btn.click(emotion, inputs=emo_input, outputs=emo_output)
    
    with gr.Tab("Crisis"):
        cris_input = gr.Textbox(label="Teks")
        cris_output = gr.JSON(label="Hasil Krisis")
        cris_btn = gr.Button("Deteksi")
        cris_btn.click(crisis, inputs=cris_input, outputs=cris_output)
    
    gr.Markdown("---")
    gr.Markdown("API Docs: /docs")

demo.launch()
```

**Step 3: requirements.txt**

```txt
gradio>=4.0.0
fastapi>=0.110.0
uvicorn>=0.27.0
groq>=0.4.0
python-dotenv>=1.0.0
torch>=2.2.0
transformers>=4.40.0
scikit-learn>=1.4.0
elevenlabs>=1.50.0
```

**Step 4: Push dan Deploy**

```bash
git add .
git commit -m "Gradio version"
git push
```

---

#### 9.3.3 Cara Deploy Model Saja (tanpa API) - Lebih Simple

Kalau yang mau di-deploy hanya model ML (bukan API), ini cara termudah:

##### Step 1: Persiapan

```bash
# Install HuggingFace Hub
pip install huggingface_hub
```

##### Step 2: Upload dengan Python

Buat `upload_models.py`:

```python
# upload_models.py
from huggingface_hub import HfApi, create_repo
import os

# Login
api = HfApi()
token = os.getenv("HF_TOKEN")  # Dari settings/tokens

# Define models
models = [
    {
        "name": "karuna-emotion",
        "path": "models/emotion_engine/final",
        "description": "Emotion detection model untuk KarunaAI"
    },
    {
        "name": "karuna-crisis", 
        "path": "models/crisis_detector/final",
        "description": "Crisis detection model untuk KarunaAI"
    }
]

for model in models:
    repo_id = f"yourusername/{model['name']}"
    
    # Create repo
    create_repo(
        repo_id=repo_id,
        token=token,
        repo_type="model",
        exist_ok=True
    )
    
    # Upload
    api.upload_folder(
        folder_path=model["path"],
        repo_id=repo_id,
        repo_type="model",
        token=token
    )
    
    print(f"✅ Uploaded: {repo_id}")
```

##### Step 3: Run

```bash
HF_TOKEN=your_token python upload_models.py
```

---

#### 9.3.4 Cara Developer Mengakses KarunaAI di HuggingFace

##### Akses Method 1: Menggunakan Model via HuggingFace Hub

```python
# Install
pip install transformers torch

# Load model
from transformers import AutoModel, AutoTokenizer

model_name = "yourusername/karuna-emotion"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

# Inference
text = "Aku merasa sedih sekali"
inputs = tokenizer(text, return_tensors="pt")
outputs = model(**inputs)
print(outputs)
```

##### Acess Method 2: Menggunakan Spaces API

```python
# Via HTTP requests
import requests

# Chat endpoint
response = requests.post(
    "https://yourusername-karuna-ai.hf.space/chat",
    json={"message": "Halo, aku mau curhat"}
)
print(response.json())

# Emotion detection
response = requests.post(
    "https://yourusername-karuna-ai.hf.space/emotion", 
    json={"text": "Aku senang"}
)
print(response.json())
```

##### Access Method 3: Menggunakan Gradio Client

```python
# Install Gradio client
pip install gradio_client

# Connect ke Space
from gradio_client import Client

client = Client("https://yourusername-karuna-ai.hf.space")

# Chat
result = client.predict(
    "Halo, aku mau curhat",
    fn_index=0  # Chat function index
)
print(result)

# Emotion
result = client.predict(
    "Aku merasa sedih",
    fn_index=1  # Emotion function index
)
print(result)
```

##### Access Method 4: Via API (Space dengan FastAPI)

```python
import requests
import base64

BASE_URL = "https://yourusername-karuna-ai.hf.space"

# 1. Chat
response = requests.post(
    f"{BASE_URL}/api/v1/chat",
    json={"message": "Aku merasa lelah"}
)
data = response.json()
print(data["response"])

# 2. Emotion
response = requests.post(
    f"{BASE_URL}/api/v1/emotion",
    json={"text": "Aku senang"}
)
print(response.json())

# 3. Crisis
response = requests.post(
    f"{BASE_URL}/api/v1/crisis",
    json={"text": "Aku mau bunuh diri"}
)
print(response.json())

# 4. TTS
response = requests.post(
    f"{BASE_URL}/api/v1/tts",
    json={"text": "Halo", "voice": "sarah"}
)
audio = base64.b64decode(response.json()["audio"])
# Play audio
```

---

#### 9.3.5 Perbandingan Deployment Options

| Aspect | Model Only | Gradio Space | Docker Space |
|--------|-----------|-------------|--------------|--------------|
| **Biaya** | Free | Free | Free (with limits) |
| **API** | ❌ | ✅ (Gradio) | ✅ (FastAPI) |
| **GPU** | ✅ | ⚠️ Limited | ✅ |
| **Complexity** | Easy | Medium | Harder |
| **Developer Access** | Download model | HTTP/Client | Full REST API |
| **Best untuk** | ML researchers | Demo/Testing | Production |

---

#### 9.3.6 Troubleshooting HuggingFace

| Issue | Solution |
|-------|----------|
| Model too large | Use git LFS: `git lfs install` |
| Build failed | Check requirements.txt |
| Out of memory | Reduce batch size |
| Slow inference | Upgrade to GPU hardware |
| Secret not found | Check Space secrets settings |

---

## 10. Testing API (Sebelum Deploy)

### 8.1 API Testing Script

Buat file `tests/test_api.py`:

```python
# tests/test_api.py
# Integration tests untuk KarunaAI API

import requests
import base64
import pytest

BASE_URL = "http://localhost:8000/api/v1"
API_KEY = None  # Set if API key enabled


def get_headers():
    """Get headers for requests."""
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["X-API-Key"] = API_KEY
    return headers


def test_health():
    """Test health endpoint."""
    r = requests.get(f"{BASE_URL.replace('/api/v1', '')}/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


def test_emotion():
    """Test emotion detection."""
    r = requests.post(
        f"{BASE_URL}/emotion",
        json={"text": "Aku merasa sangat senang hari ini!"},
        headers=get_headers()
    )
    assert r.status_code == 200
    data = r.json()
    assert "dominant" in data
    assert "score" in data
    assert "distress_score" in data


def test_crisis():
    """Test crisis detection."""
    r = requests.post(
        f"{BASE_URL}/crisis",
        json={"text": "Aku mau bunuh diri"},
        headers=get_headers()
    )
    assert r.status_code == 200
    data = r.json()
    assert data["level"] == "L3"


def test_chat():
    """Test chat endpoint."""
    r = requests.post(
        f"{BASE_URL}/chat",
        json={"message": "Halo, aku merasa lelah"},
        headers=get_headers()
    )
    assert r.status_code == 200
    data = r.json()
    assert "response" in data
    assert "emotion" in data
    assert "crisis" in data


def test_tts():
    """Test TTS endpoint."""
    # Note: Requires Eleven Labs API key
    r = requests.post(
        f"{BASE_URL}/tts",
        json={"text": "Halo, aku Karuna.", "voice": "sarah"},
        headers=get_headers()
    )
    if r.status_code == 200:
        data = r.json()
        assert "audio" in data


def test_stt():
    """Test STT endpoint."""
    # Create test audio file first
    # Then test
    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

### 8.2 Load Testing

Buat file `tests/load_test.py`:

```python
# tests/load_test.py
# Load testing menggunakan locust

from locust import HttpUser, task, between
import random


class KarunaAIUser(HttpUser):
    wait_time = between(1, 3)
    
    messages = [
        "Aku merasa lelah banget",
        "Hari ini aku senang bisa cerita sama kamu",
        "Masalah kerjaan numpuk",
        "Aku bingung sama hubungan aku",
    ]
    
    @task(3)
    def chat(self):
        self.client.post(
            "/api/v1/chat",
            json={"message": random.choice(self.messages)},
            headers={"X-API-Key": ""}  # Add API key if needed
        )
    
    @task(2)
    def emotion(self):
        self.client.post(
            "/api/v1/emotion",
            json={"text": random.choice(self.messages)},
            headers={"X-API-Key": ""}
        )
    
    @task(1)
    def crisis(self):
        self.client.post(
            "/api/v1/crisis",
            json={"text": random.choice(self.messages)},
            headers={"X-API-Key": ""}
        )
```

Run dengan:

```bash
pip install locust
locust -f tests/load_test.py --host http://localhost:8000
```

---

## 11. Developer Documentation (Untuk consumer API)

### 9.1 Quick Start Guide

Buat file `API.md`:

```markdown
# KarunaAI API Documentation

## Base URL

```
https://your-api.onrender.com/api/v1
```

## Authentication

Jika API key diaktifkan, tambahkan header:

```
X-API-Key: your_api_key
```

## Endpoints

### 1. Chat — Kirim Pesan

```bash
curl -X POST https://your-api.onrender.com/api/v1/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{"message": "Aku merasa lelah"}'
```

**Response:**
```json
{
  "response": "Aku mendengar...",
  "emotion": {
    "dominant": "sadness",
    "score": 0.75,
    "distress_score": 0.6
  },
  "crisis": {
    "level": "NORMAL",
    "score": 0.1
  },
  "session_id": "abc123"
}
```

### 2. Emotion — Deteksi Emosi

```bash
curl -X POST https://your-api.onrender.com/api/v1/emotion \
  -H "Content-Type: application/json" \
  -d '{"text": "Aku senang bisa ketemu kamu"}'
```

### 3. Crisis — Deteksi Krisis

```bash
curl -X POST https://your-api.onrender.com/api/v1/crisis \
  -H "Content-Type: application/json" \
  -d '{"text": "Aku mau bunuh diri"}'
```

### 4. TTS — Teks ke Audio

```bash
curl -X POST https://your-api.onrender.com/api/v1/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Halo, aku Karuna", "voice": "sarah"}'
```

### 5. STT — Audio ke Teks

```bash
curl -X POST https://your-api.onrender.com/api/v1/stt \
  -H "Content-Type: application/json" \
  -d '{"audio": "base64_encoded_audio"}'
```

## Error Codes

| Code | Meaning |
|------|---------|
| 400 | Bad Request - input tidak valid |
| 401 | Unauthorized - API key diperlukan |
| 403 | Forbidden - API key tidak valid |
| 429 | Too Many Requests - rate limit exceeded |
| 500 | Internal Server Error |

## Rate Limits

- Default: 60 requests/minute
- Per API key: 1000 requests/hour

## Code Examples

### Python

```python
import requests

BASE_URL = "https://your-api.onrender.com/api/v1"

def chat(message):
    response = requests.post(
        f"{BASE_URL}/chat",
        json={"message": message},
        headers={"X-API-Key": "your_api_key"}
    )
    return response.json()

result = chat("Aku merasa lelah")
print(result["response"])
```

### JavaScript

```javascript
const response = await fetch('https://your-api.onrender.com/api/v1/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'your_api_key'
  },
  body: JSON.stringify({ message: 'Aku merasa lelah' })
});

const result = await response.json();
console.log(result.response);
```

### cURL

```bash
# Chat
curl -X POST https://your-api.onrender.com/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Halo"}'

# Emotion detection
curl -X POST https://your-api.onrender.com/api/v1/emotion \
  -H "Content-Type: application/json" \
  -d '{"text": "Aku senang"}'

# TTS
curl -X POST https://your-api.onrender.com/api/v1/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Halo", "voice": "sarah"}'
```
```

### 9.2 Integration Examples

Buat file `examples/README.md`:

```markdown
# KarunaAI Integration Examples

## React Integration

```jsx
// React component
import { useState } from 'react';

function KarunaChat() {
  const [messages, setMessages] = useState([]);
  
  const sendMessage = async (text) => {
    const response = await fetch('/api/v1/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': 'your_api_key'
      },
      body: JSON.stringify({ message: text })
    });
    
    const data = await response.json();
    setMessages([...messages, { text, response: data.response }]);
  };
  
  return (
    <div>
      {messages.map(m => (
        <div>
          <p>User: {m.text}</p>
          <p>Karuna: {m.response}</p>
        </div>
      ))}
    </div>
  );
}
```

## Vue.js Integration

```javascript
// Vue component
export default {
  data() {
    return { messages: [] }
  },
  methods: {
    async sendMessage(text) {
      const response = await fetch('/api/v1/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': 'your_api_key'
        },
        body: JSON.stringify({ message: text })
      });
      
      const data = await response.json();
      this.messages.push({ text, response: data.response });
    }
  }
}
```

## Mobile (React Native)

```javascript
// React Native
import { fetch } from 'react-native';

async function sendMessage(text) {
  const response = await fetch('https://your-api.onrender.com/api/v1/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': 'your_api_key'
    },
    body: JSON.stringify({ message: text })
  });
  
  return response.json();
}
```

## Voice Integration

### STT → KarunaAI → TTS

```python
# Full pipeline
import base64

# 1. Record audio
audio = record_from_microphone()

# 2. STT
stt_response = await fetch('/api/v1/stt', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({audio: base64.b64encode(audio).decode()})
})
text = stt_response.json()['text']

# 3. Chat
chat_response = await fetch('/api/v1/chat', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({message: text})
})
response_text = chat_response.json()['response']

# 4. TTS
tts_response = await fetch('/api/v1/tts', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({text: response_text, voice: 'sarah'})
})
audio_base64 = tts_response.json()['audio']

# 5. Play audio
play_audio(base64.b64decode(audio_base64))
```
```

---

## 10. Security Checklist

### 10.1 Pre-Production Security

- [ ] API key authentication enabled
- [ ] Rate limiting configured
- [ ] CORS configured untuk domain yang benar
- [ ] Environment variables tidak di-commit
- [ ] Debug mode disabled
- [ ] Health check endpoint read-only
- [ ] Input validation implemented
- [ ] Output sanitization implemented
- [ ] Error messages don't expose internals
- [ ] HTTPS enforced (use platform's SSL)
- [ ] Logging configured (tidak log sensitive data)
- [ ] Session timeout configured

### 10.2 API Key Best Practices

1. **Generate secure keys**
```bash
python -c "import secrets; print('ka_' + secrets.token_urlsafe(32))"
```

2. **Rotate regularly**
```bash
# Generate new key
NEW_KEY=$(python -c "import secrets; print('ka_' + secrets.token_urlsafe(32))")

# Update in system
# Add new key first, then remove old key
```

3. **Use separate keys per application**
```python
# Environment-specific API keys
API_KEYS=prod_key_1,dev_key_2,test_key_3
```

---

## 11. Troubleshooting

### 11.1 Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| 500 Internal Server Error | Model not loaded | Check model paths |
| 401 Unauthorized | API key not provided | Add header `X-API-Key` |
| 403 Forbidden | Invalid API key | Verify API key |
| 429 Too Many Requests | Rate limit | Wait and retry |
| Connection timeout | Cold start | Increase timeout |
| STT/TTS fails | Missing API key | Check ELEVENLABS_API_KEY |

### 11.2 Debug Mode

Enable debug untuk melihat error details:

```bash
DEBUG=true
```

### 11.3 Health Check

```bash
curl https://your-api.onrender.com/health
```

### 11.4 Logs

View logs di Render dashboard:
- Dashboard → Your service → Logs

---

## 12. Step-by-Step Implementation Summary

### Phase 1: Prepare (1-2 jam)

1. [ ] Install dependencies
   ```bash
   pip install -r requirements-api.txt
   ```

2. [ ] Setup environment variables
   ```bash
   cp .env.example .env
   # Edit .env dengan API keys
   ```

3. [ ] Test locally
   ```bash
   uvicorn api.main:app --reload
   ```

### Phase 2: Dockerize (1 jam)

1. [ ] Create Dockerfile
2. [ ] Test Docker build
   ```bash
   docker build -f docker/Dockerfile -t karuna-api .
   ```

3. [ ] Test Docker run
   ```bash
   docker run -p 8000:8000 --env-file .env karuna-api
   ```

### Phase 3: Deploy (1-2 jam)

1. [ ] Push ke GitHub
2. [ ] Setup Render account
3. [ ] Create web service
4. [ ] Set environment variables
5. [ ] Deploy
6. [ ] Test production endpoint

### Phase 4: Documentation (1 jam)

1. [ ] Update API.md
2. [ ] Create integration examples
3. [ ] Test dengan developer scenario
4. [ ] Share dengan developers

---

## 📞 Support

Jika ada pertanyaan atau issues:

- **Documentation**: Lihat `API.md`
- **Issues**: https://github.com/yourusername/karunaAI/issues
- **Email**: support@karuna.ai

---

## Lisensi

MIT License - Silakan gunakan sesuai kebutuhan.

---

*Last Updated: April 2026*