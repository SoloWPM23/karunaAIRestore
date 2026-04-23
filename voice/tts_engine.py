# voice/tts_engine.py
# Text-to-Speech Engine menggunakan Eleven Labs API

import os
import io
import threading
from typing import Optional
from dotenv import load_dotenv

from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

load_dotenv()

# ── Eleven Labs client ────────────────────────────────────────────────────
_client: Optional[ElevenLabs] = None
_LOCK = threading.Lock()


def _get_client() -> ElevenLabs:
    """Get atau create Eleven Labs client."""
    global _client
    if _client is None:
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            raise ValueError("ELEVENLABS_API_KEY tidak ditemukan di environment variables")
        _client = ElevenLabs(api_key=api_key)
    return _client


# ── Konfigurasi Voice ─────────────────────────────────────────────────────
# Eleven Labs Multilingual Voices yang cocok untuk Bahasa Indonesia
# Beberapa voice yang recommended untuk bahasa Indonesia:
# - "Sarah" - Female, warm, natural (multilingual v2)
# - "Charlotte" - Female, calm, soothing
# - "Aria" - Female, expressive
# - "Roger" - Male, professional

DEFAULT_VOICE_ID = "3AwU3nHsI4YWeBJbz6yn"  # Honeypie - Female
DEFAULT_MODEL = "eleven_v3"  # Support bahasa Indonesia

# Voice IDs untuk pilihan
AVAILABLE_VOICES = {
    "sarah": "EXAVITQu4vr4xnSDxMaL",      # Female, warm (recommended)
    "charlotte": "XB0fDUnXU5powFXDhCwa",  # Female, calm
    "aria": "9BWtsMINqrJLrRacOk9x",       # Female, expressive
    "roger": "CwhRBWXzGAHq8TQ4Fs17",      # Male, professional
    "jessica": "cgSgspJ2msm6clMCkdW9",    # Female, conversational
    "brian": "nPczCjzI2devNBz1zQrb",      # Male, deep
    "gavrila": "gjhfBUoH6DHh0DG1X4u0",     # Female, young, warm
    "honeypie": "3AwU3nHsI4YWeBJbz6yn"
}


class TTSEngine:
    """
    Text-to-Speech Engine menggunakan Eleven Labs API.

    Fitur:
    - Suara natural berkualitas tinggi
    - Support Bahasa Indonesia (multilingual v2)
    - Kontrol stability, similarity, style, dan speed
    - Thread-safe
    """

    def __init__(
        self,
        voice_id: str = DEFAULT_VOICE_ID,
        model_id: str = DEFAULT_MODEL,
        stability: float = 0.65,
        similarity_boost: float = 0.8,
        style: float = 0.15,
        use_speaker_boost: bool = True,
        speed: float = 0.87,
    ):
        self.voice_id = voice_id
        self.model_id = model_id
        self.stability = stability
        self.similarity_boost = similarity_boost
        self.style = style
        self.use_speaker_boost = use_speaker_boost
        self.speed = speed

    def _get_voice_settings(self) -> VoiceSettings:
        """Build voice settings dari parameter engine."""
        return VoiceSettings(
            stability=self.stability,
            similarity_boost=self.similarity_boost,
            style=self.style,
            use_speaker_boost=self.use_speaker_boost,
        )

    def synthesize(self, text: str) -> bytes:
        """
        Synthesize text ke audio bytes.

        Args:
            text: Teks yang akan diubah ke suara

        Returns:
            Audio dalam format MP3 bytes
        """
        if not text.strip():
            return b""

        with _LOCK:
            client = _get_client()

            # Build parameters untuk API call
            params = {
                "voice_id": self.voice_id,
                "text": text,
                "model_id": self.model_id,
                "voice_settings": self._get_voice_settings(),
                "output_format": "mp3_44100_128",
            }

            # Coba tambahkan speed jika didukung oleh versi elevenlabs
            try:
                audio_generator = client.text_to_speech.convert(
                    **params,
                    speed=self.speed,
                )
            except TypeError:
                # Fallback jika speed tidak didukung
                audio_generator = client.text_to_speech.convert(**params)

            # Collect all chunks into bytes
            audio_chunks = []
            for chunk in audio_generator:
                audio_chunks.append(chunk)

            return b"".join(audio_chunks)

    def save(self, text: str, output_path: str) -> str:
        """
        Synthesize dan simpan ke file.

        Args:
            text: Teks yang akan diubah ke suara
            output_path: Path file output (MP3)

        Returns:
            Path file yang disimpan
        """
        audio_bytes = self.synthesize(text)
        with open(output_path, "wb") as f:
            f.write(audio_bytes)
        return output_path

    def save_temp(self, text: str) -> str:
        """
        Synthesize dan simpan ke temp file.

        Args:
            text: Teks yang akan diubah ke suara

        Returns:
            Path temp file (caller harus cleanup)
        """
        import tempfile
        tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        tmp.close()
        return self.save(text, tmp.name)

    def set_voice(self, voice_id: str):
        """Ganti voice menggunakan voice ID."""
        self.voice_id = voice_id

    def set_voice_by_name(self, name: str):
        """
        Ganti voice menggunakan nama preset.

        Args:
            name: Nama voice ("sarah", "charlotte", "aria", "roger", dll)
        """
        if name.lower() in AVAILABLE_VOICES:
            self.voice_id = AVAILABLE_VOICES[name.lower()]
        else:
            raise ValueError(f"Voice '{name}' tidak ditemukan. Pilihan: {list(AVAILABLE_VOICES.keys())}")

    def set_stability(self, stability: float):
        """
        Set stability suara (0.0 - 1.0).

        - Rendah (0.0-0.3): Lebih ekspresif, variatif
        - Sedang (0.3-0.7): Seimbang
        - Tinggi (0.7-1.0): Lebih konsisten, stabil
        """
        self.stability = max(0.0, min(1.0, stability))

    def set_similarity_boost(self, similarity: float):
        """
        Set similarity boost (0.0 - 1.0).

        Semakin tinggi, semakin mirip dengan voice asli.
        """
        self.similarity_boost = max(0.0, min(1.0, similarity))

    def set_style(self, style: float):
        """
        Set style exaggeration (0.0 - 1.0).

        Semakin tinggi, semakin ekspresif.
        """
        self.style = max(0.0, min(1.0, style))

    def set_speed(self, speed: float):
        """
        Set kecepatan bicara (0.5 - 2.0).

        - 0.5: Sangat lambat (50% kecepatan normal)
        - 1.0: Normal
        - 1.5: Cepat (150% kecepatan normal)
        - 2.0: Sangat cepat (200% kecepatan normal)
        """
        self.speed = max(0.5, min(2.0, speed))


# ── Default instance ──────────────────────────────────────────────────────
_default_engine: Optional[TTSEngine] = None


def get_engine() -> TTSEngine:
    """Get atau create default TTS engine."""
    global _default_engine
    if _default_engine is None:
        _default_engine = TTSEngine()
    return _default_engine


def speak(text: str) -> bytes:
    """
    Quick function untuk synthesize text.

    Args:
        text: Teks yang akan diubah ke suara

    Returns:
        Audio dalam format MP3 bytes
    """
    return get_engine().synthesize(text)


def speak_to_file(text: str, output_path: str) -> str:
    """
    Quick function untuk synthesize dan save ke file.

    Args:
        text: Teks yang akan diubah ke suara
        output_path: Path file output

    Returns:
        Path file yang disimpan
    """
    return get_engine().save(text, output_path)


def list_voices() -> dict:
    """Daftar voice yang tersedia."""
    return AVAILABLE_VOICES.copy()


# ── Presets untuk mood ────────────────────────────────────────────────────
# Eleven Labs menggunakan stability, style, dan speed untuk mengatur mood
MOOD_PRESETS = {
    "calm": {
        "stability": 0.7,
        "similarity_boost": 0.75,
        "style": 0.1,
        "speed": 0.9,
    },
    "warm": {
        "stability": 0.5,
        "similarity_boost": 0.75,
        "style": 0.2,
        "speed": 1.0,
    },
    "gentle": {
        "stability": 0.8,
        "similarity_boost": 0.8,
        "style": 0.05,
        "speed": 0.85,
    },
    "concerned": {
        "stability": 0.4,
        "similarity_boost": 0.7,
        "style": 0.3,
        "speed": 0.95,
    },
}


def apply_mood(engine: TTSEngine, mood: str):
    """
    Apply mood preset ke engine.

    Args:
        engine: TTSEngine instance
        mood: Nama mood ("calm", "warm", "gentle", "concerned")
    """
    if mood in MOOD_PRESETS:
        preset = MOOD_PRESETS[mood]
        engine.set_stability(preset["stability"])
        engine.set_similarity_boost(preset["similarity_boost"])
        engine.set_style(preset["style"])
        engine.set_speed(preset["speed"])
