# voice/__init__.py
# Voice module untuk KarunaAI — STT & TTS

from voice.stt_engine import (
    AudioRecorder,
    transcribe_audio,
    transcribe_file,
    record_and_transcribe,
)

from voice.tts_engine import (
    TTSEngine,
    get_engine,
    speak,
    speak_to_file,
    apply_mood,
    list_voices,
    AVAILABLE_VOICES,
    MOOD_PRESETS,
)

__all__ = [
    # STT
    "AudioRecorder",
    "transcribe_audio",
    "transcribe_file",
    "record_and_transcribe",
    # TTS
    "TTSEngine",
    "get_engine",
    "speak",
    "speak_to_file",
    "apply_mood",
    "list_voices",
    "AVAILABLE_VOICES",
    "MOOD_PRESETS",
]
