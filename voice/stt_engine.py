# voice/stt_engine.py
# Speech-to-Text Engine menggunakan Eleven Labs API

import os
import io
import tempfile
import threading
from typing import Optional
import numpy as np
import sounddevice as sd
from scipy.io import wavfile
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv

load_dotenv()

# ── Eleven Labs client untuk STT API ──────────────────────────────────────
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

# ── Konfigurasi audio ─────────────────────────────────────────────────────
SAMPLE_RATE = 16000  # Standard sample rate untuk STT
CHANNELS = 1
DTYPE = np.int16


class AudioRecorder:
    """
    Merekam audio dari mikrofon.

    Usage:
        recorder = AudioRecorder()
        recorder.start()
        # ... user berbicara ...
        recorder.stop()
        audio_bytes = recorder.get_wav_bytes()
    """

    def __init__(self, sample_rate: int = SAMPLE_RATE):
        self.sample_rate = sample_rate
        self.recording = False
        self.frames: list = []
        self._stream = None

    def _callback(self, indata, frames, time, status):
        """Callback untuk sounddevice stream."""
        if self.recording:
            self.frames.append(indata.copy())

    def start(self):
        """Mulai merekam audio."""
        self.frames = []
        self.recording = True
        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=CHANNELS,
            dtype=DTYPE,
            callback=self._callback,
        )
        self._stream.start()

    def stop(self):
        """Stop rekaman dan kembalikan audio."""
        self.recording = False
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

    def get_wav_bytes(self) -> bytes:
        """
        Konversi frames yang direkam ke format WAV bytes.

        Returns:
            WAV file sebagai bytes, siap dikirim ke Eleven Labs STT API
        """
        if not self.frames:
            return b""

        audio_data = np.concatenate(self.frames, axis=0)

        # Tulis ke buffer sebagai WAV
        buffer = io.BytesIO()
        wavfile.write(buffer, self.sample_rate, audio_data)
        buffer.seek(0)
        return buffer.read()

    def get_duration(self) -> float:
        """Durasi rekaman dalam detik."""
        if not self.frames:
            return 0.0
        total_samples = sum(len(f) for f in self.frames)
        return total_samples / self.sample_rate


def transcribe_audio(audio_bytes: bytes, language: str = "id") -> str:
    """
    Transkripsi audio menggunakan Eleven Labs STT API.

    Args:
        audio_bytes: Audio dalam format WAV bytes
        language: Kode bahasa (default "id" untuk Indonesia)

    Returns:
        Teks hasil transkripsi
    """
    if not audio_bytes:
        return ""

    # Simpan ke temp file karena API butuh file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        with _LOCK:
            client = _get_client()
            with open(tmp_path, "rb") as audio_file:
                result = client.speech_to_text.convert(
                    file=audio_file,
                    model_id="scribe_v1",
                    language_code=language,
                )
        # Result adalah SpeechToTextChunkResponse dengan atribut text
        return result.text.strip() if hasattr(result, 'text') else str(result).strip()

    except Exception as e:
        print(f"[STT] Error transcribing: {e}")
        return ""

    finally:
        # Cleanup temp file
        try:
            os.unlink(tmp_path)
        except:
            pass


def transcribe_file(file_path: str, language: str = "id") -> str:
    """
    Transkripsi file audio menggunakan Eleven Labs STT API.

    Args:
        file_path: Path ke file audio (WAV, MP3, dll)
        language: Kode bahasa

    Returns:
        Teks hasil transkripsi
    """
    try:
        with _LOCK:
            client = _get_client()
            with open(file_path, "rb") as audio_file:
                result = client.speech_to_text.convert(
                    file=audio_file,
                    model_id="scribe_v1",
                    language_code=language,
                )
        return result.text.strip() if hasattr(result, 'text') else str(result).strip()

    except Exception as e:
        print(f"[STT] Error transcribing file: {e}")
        return ""


# ── Convenience function untuk quick recording ────────────────────────────
def record_and_transcribe(duration: float = 5.0, language: str = "id") -> str:
    """
    Rekam audio selama durasi tertentu dan transkripsi menggunakan Eleven Labs.

    Args:
        duration: Durasi rekaman dalam detik
        language: Kode bahasa

    Returns:
        Teks hasil transkripsi
    """
    print(f"[STT] Recording for {duration}s...")

    # Rekam audio
    audio_data = sd.rec(
        int(duration * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype=DTYPE,
    )
    sd.wait()

    print("[STT] Recording complete. Transcribing...")

    # Konversi ke WAV bytes
    buffer = io.BytesIO()
    wavfile.write(buffer, SAMPLE_RATE, audio_data)
    buffer.seek(0)
    audio_bytes = buffer.read()

    return transcribe_audio(audio_bytes, language)
