# orchestrator.py
# Pipeline utama KarunaAI — menggabungkan S1 + S2 + S3 + S4
#
# Alur per pesan:
#
#   user_input
#       │
#       ├─▶ [S2] EmotionEngine.analyze()     → EmotionResult
#       │         (distress_score, dominant, topics, distribution)
#       │
#       ├─▶ [S3] analyze_crisis()            → CDSResult
#       │         (level, score, triggers, detail)
#       │         menggunakan emotion_history untuk Layer 3
#       │
#       ├─▶ [S1] build_system_prompt()
#       │         chat_with_groq()          → ai_response (str)
#       │
#       └─▶ [S1] validate()                 → (is_valid, reason)
#
# Alur akhir sesi:
#       └─▶ [S4] generate_summary()          → SessionSummary

from dataclasses import dataclass, field
from typing import Any, Optional
from s1_conversational.prompt_builder   import build_system_prompt
from s1_conversational.groq_client      import chat_with_groq
from s1_conversational.output_validator import validate
from s2_emotion.emotion_engine          import EmotionEngine
from s3_crisis.cds_engine              import analyze_crisis
from s4_summary.summary_generator      import generate_summary, SessionSummary

# ── Output per pesan ───────────────────────────────────────────────────────
@dataclass
class TurnResult:
    """Hasil pemrosesan satu pesan user."""
    ai_response    : str
    emotion_result : object        # EmotionResult dari S2
    cds_result     : object        # CDSResult dari S3
    is_valid       : bool
    validator_note : str
    crisis_banner  : str = ""      # "" / "L2" / "L3" untuk UI

# ── Orchestrator class ─────────────────────────────────────────────────────
class KarunaOrchestrator:
    """
    Mengelola state sesi dan mengorkestrasi semua subsistem.

    Satu instance per sesi (disimpan di Streamlit session_state).
    """

    def __init__(self, emotion_engine: EmotionEngine):
        self.emotion_engine   : EmotionEngine = emotion_engine

        # State sesi
        self.messages         : list = []   # Riwayat untuk Groq API
        self.chat_log         : list = []   # Riwayat untuk UI {"role", "content"}
        self.emotion_history  : list = []   # List EmotionResult
        self.recent_closings  : list = []   # Kalimat penutup untuk anti-repetisi
        self.msg_count        : int  = 0
        self.last_cds_result  : Any = None
        self.last_valid       : bool = True
        self.last_reason      : str  = ""
        self.session_ended    : bool = False
        self.summary          : Optional[SessionSummary] = None

    # ── Proses satu pesan ─────────────────────────────────────────────────
    def process(self, user_input: str) -> TurnResult:
        """
        Jalankan pipeline lengkap untuk satu pesan user.

        Returns:
            TurnResult berisi respons AI dan semua metadata
        """
        if self.session_ended:
            raise RuntimeError("Sesi sudah diakhiri. Mulai sesi baru.")

        self.msg_count += 1

        # ── S2: Emotion Engine ────────────────────────────────────────────
        try:
            emotion_result = self.emotion_engine.analyze(user_input)
            self.emotion_history.append(emotion_result)
        except Exception as e:
            # Fallback: default neutral emotion if S2 fails
            from s2_emotion.emotion_engine import EmotionResult
            emotion_result = EmotionResult(
                dominant="netral",
                score=1.0,
                distribution={"netral": 1.0, "senang": 0.0, "sedih": 0.0, "marah": 0.0, "takut": 0.0, "kaget": 0.0, "jijik": 0.0},
                topics=["other"],
                distress_score=0.0
            )
            self.emotion_history.append(emotion_result)
            print(f"[S2] EmotionEngine failed: {e}")

        # ── S3: Crisis Detection (L1 + L2 + L3) ──────────────────────────
        try:
            cds_result = analyze_crisis(
                text=user_input,
                emotion_history=self.emotion_history,
            )
            self.last_cds_result = cds_result
        except Exception as e:
            # Fallback: NORMAL level if S3 fails
            from s3_crisis.cds_engine import CDSResult
            cds_result = CDSResult(
                level="NORMAL",
                score=0.0,
                triggers=[],
                detail={"error": str(e)}
            )
            self.last_cds_result = cds_result
            print(f"[S3] CDS failed: {e}")

        # ── Koreksi distress: CDS sebagai floor distress_score ────────────
        # S2 (EmotionEngine) menilai emosi secara isolated per kalimat.
        # Kalimat seperti "tali 2 meter memanggilku" bisa punya distress
        # rendah dari S2 meski sinyal krisis sangat kuat dari S3.
        # CDS level dijadikan floor minimum distress_score.
        CDS_DISTRESS_FLOOR = {"NORMAL": 0.0, "L1": 0.35, "L2": 0.60, "L3": 0.85}
        floor = CDS_DISTRESS_FLOOR.get(cds_result.level, 0.0)
        if emotion_result.distress_score < floor:
            emotion_result.distress_score = floor

        # ── S1: Build prompt & generate respons ───────────────────────────
        try:
            # Extract user messages untuk detect speaking style
            user_messages = [msg["content"] for msg in self.chat_log if msg["role"] == "user"]
            recent_assistant_messages = [
                msg["content"] for msg in self.chat_log if msg["role"] == "assistant"
            ]

            system_prompt = build_system_prompt(
                dominant_emotion = emotion_result.dominant,
                emotion_score    = emotion_result.score,
                cds_level        = cds_result.level,
                message_count    = self.msg_count,
                topics           = emotion_result.topics,
                recent_closings  = self.recent_closings,
                user_messages    = user_messages,  # NEW: untuk adaptasi gaya bicara
                recent_assistant_messages = recent_assistant_messages,
            )

            ai_response = chat_with_groq(
                system_prompt,
                self.messages,
                user_input,
            )
        except Exception as e:
            ai_response = "Maaf, aku sedang mengalami kesulitan teknis. Bisakah kamu ulangi pesanmu?"
            print(f"[S1] Groq failed: {e}")

        # ── S1: Validasi output ───────────────────────────────────────────
        is_valid, reason = validate(ai_response, cds_level=cds_result.level)
        self.last_valid  = is_valid
        self.last_reason = reason

        # ── Tracking kalimat penutup (anti-repetisi) ──────────────────────
        sentences = [s.strip() for s in ai_response.replace("\n", " ").split(".") if s.strip()]
        if sentences:
            last_sent = sentences[-1]
            if len(last_sent.split()) >= 4:
                self.recent_closings.append(last_sent)
                self.recent_closings = self.recent_closings[-3:]

        # ── Update riwayat ────────────────────────────────────────────────
        self.messages.append({"role": "user", "content": user_input})
        self.messages.append({"role": "assistant", "content": ai_response})
        self.chat_log.append({"role": "user",      "content": user_input})
        self.chat_log.append({"role": "assistant", "content": ai_response})

        # ── Tentukan banner UI ────────────────────────────────────────────
        crisis_banner = ""
        if cds_result.level == "L3":
            crisis_banner = "L3"
        elif cds_result.level == "L2":
            crisis_banner = "L2"

        return TurnResult(
            ai_response    = ai_response,
            emotion_result = emotion_result,
            cds_result     = cds_result,
            is_valid       = is_valid,
            validator_note = reason,
            crisis_banner  = crisis_banner,
        )

    # ── Akhiri sesi & generate summary ────────────────────────────────────
    def end_session(self) -> Optional[SessionSummary]:
        """
        Akhiri sesi dan generate ringkasan via S4.

        Returns:
            SessionSummary — None jika sesi kosong (0 pesan)
        """
        if self.msg_count == 0:
            return None

        self.session_ended = True

        cds_level = self.last_cds_result.level if self.last_cds_result else "NORMAL"
        chat_log_snapshot = [dict(m) for m in self.chat_log]
        emotion_snapshot = list(self.emotion_history)

        try:
            self.summary = generate_summary(
                chat_log        = chat_log_snapshot,
                emotion_history = emotion_snapshot,
                cds_level       = cds_level,
            )
        except Exception as e:
            # Fallback: basic summary if S4 fails
            from s4_summary.summary_generator import SessionSummary
            self.summary = SessionSummary(
                flag="MEDIUM",
                flag_reasoning="Summary generation failed - manual review diperlukan.",
                paragraf="Sesi berlangsung namun sistem tidak dapat menghasilkan ringkasan otomatis. Mohon review manual chat log.",
                pesan_penutup="Terima kasih sudah berbagi. Semoga kamu merasa sedikit lebih ringan.",
                tren_distress="unknown",
                distress_awal=0.0,
                distress_akhir=0.0,
                jumlah_pesan=self.msg_count,
                cds_level_akhir=cds_level
            )
            print(f"[S4] Summary failed: {e}")

        return self.summary

    # ── Reset sesi baru ───────────────────────────────────────────────────
    def reset(self):
        """Reset semua state untuk memulai sesi baru."""
        self.messages        = []
        self.chat_log        = []
        self.emotion_history = []
        self.recent_closings = []
        self.msg_count       = 0
        self.last_cds_result = None
        self.last_valid      = True
        self.last_reason     = ""
        self.session_ended   = False
        self.summary         = None