# demo/app_voice.py
# KarunaAI Voice Demo - custom HTML/CSS redesign with production-ready flow

import os
import time
import base64
from pathlib import Path
from textwrap import dedent

os.environ["USE_TF"] = "0"
os.environ["USE_TORCH"] = "1"

import streamlit as st

from pipeline.orchestrator import KarunaOrchestrator
from s2_emotion.emotion_engine import EmotionEngine
from s4_summary.summary_generator import delete_session_json
from voice.stt_engine import AudioRecorder, transcribe_audio
from voice.tts_engine import TTSEngine, apply_mood


WELCOME_MESSAGE = (
    "Halo, aku Karuna. Aku di sini untuk mendengarkan kamu. "
    "Kalau kamu nyaman, kamu bisa mulai cerita pelan-pelan."
)

HELP_LINE_MESSAGE = (
    "Karuna mendeteksi kondisi yang sangat berat. "
    "Jika kamu butuh bantuan segera, hubungi Into The Light: 119 ext 8 (24 jam)."
)


def configure_page() -> None:
    st.set_page_config(
        page_title="KarunaAI Voice",
        page_icon=":material/graphic_eq:",
        layout="wide",
        initial_sidebar_state="collapsed",
    )


def render_html(html: str) -> None:
    st.markdown(dedent(html).strip(), unsafe_allow_html=True)


def inject_styles() -> None:
    render_html(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

            :root {
                --bg-0: #020713;
                --bg-1: #04112b;
                --bg-2: #07234a;
                --bg-glow: rgba(53, 122, 255, 0.35);
                --surface: rgba(8, 18, 40, 0.68);
                --surface-soft: rgba(12, 29, 62, 0.72);
                --stroke: rgba(132, 170, 255, 0.22);
                --text-main: #e9f0ff;
                --text-muted: #8ea6d8;
                --accent: #5fa6ff;
                --accent-soft: rgba(95, 166, 255, 0.18);
                --danger: #ff6e78;
                --danger-soft: #ff5d69;
                --ok: #58b0ff;
            }

            @media (prefers-color-scheme: light) {
                :root {
                    --bg-0: #eaf2ff;
                    --bg-1: #f4f8ff;
                    --bg-2: #ffffff;
                    --bg-glow: rgba(67, 118, 223, 0.18);
                    --surface: rgba(255, 255, 255, 0.72);
                    --surface-soft: rgba(250, 252, 255, 0.88);
                    --stroke: rgba(98, 132, 206, 0.18);
                    --text-main: #0e234f;
                    --text-muted: #536f9e;
                    --accent: #2f7df4;
                    --accent-soft: rgba(47, 125, 244, 0.15);
                    --danger: #f55a68;
                    --danger-soft: #e8505e;
                    --ok: #1d7be8;
                }
            }

            html, body, [class*="css"] {
                font-family: 'Manrope', sans-serif;
            }

            [data-testid="stAppViewContainer"] {
                background:
                    radial-gradient(58% 38% at 50% 12%, var(--bg-glow) 0%, transparent 72%),
                    radial-gradient(40% 30% at 20% 78%, rgba(16, 54, 117, 0.28) 0%, transparent 80%),
                    linear-gradient(180deg, var(--bg-0) 0%, var(--bg-1) 56%, var(--bg-0) 100%);
                color: var(--text-main);
            }

            [data-testid="stToolbar"],
            [data-testid="stHeaderActionElements"],
            #MainMenu,
            footer {
                visibility: hidden;
                height: 0;
                position: fixed;
            }

            header[data-testid="stHeader"] {
                background: transparent;
            }

            .block-container {
                padding-top: 0.35rem;
                padding-bottom: 1.4rem;
                max-width: 1220px;
            }

            .voice-shell {
                position: relative;
                min-height: 74vh;
                border-radius: 24px;
                border: 1px solid var(--stroke);
                background: linear-gradient(160deg, var(--surface) 0%, rgba(2, 11, 28, 0.32) 100%);
                box-shadow: 0 20px 70px rgba(2, 10, 28, 0.34);
                padding: 1.1rem 1.2rem 1.2rem;
                overflow: hidden;
                margin-bottom: 1.2rem;
            }

            .voice-shell::after {
                content: "";
                position: absolute;
                width: 460px;
                height: 460px;
                right: -160px;
                top: -200px;
                background: radial-gradient(circle, rgba(76, 149, 255, 0.22), transparent 68%);
                pointer-events: none;
            }

            .voice-topbar {
                display: flex;
                align-items: center;
                justify-content: space-between;
                border-bottom: 1px solid rgba(123, 151, 214, 0.2);
                padding: 0.2rem 0.2rem 0.9rem;
                margin-bottom: 1.1rem;
            }

            .brand-group,
            .action-group {
                display: flex;
                align-items: center;
                gap: 0.75rem;
            }

            .icon-chip {
                width: 34px;
                height: 34px;
                border-radius: 50%;
                border: 1px solid rgba(133, 171, 255, 0.3);
                display: inline-flex;
                align-items: center;
                justify-content: center;
                color: var(--text-main);
                background: rgba(12, 31, 66, 0.45);
            }

            .brand-text {
                font-family: 'Space Grotesk', sans-serif;
                letter-spacing: 0.02em;
                font-weight: 700;
                color: var(--text-main);
                font-size: 1.08rem;
            }

            .action-link {
                color: var(--text-muted);
                font-size: 0.93rem;
                font-weight: 600;
                text-decoration: none;
            }

            .profile-dot {
                width: 34px;
                height: 34px;
                border-radius: 50%;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                background: linear-gradient(145deg, #3d6ebd, #203f73);
                color: #d8e7ff;
                font-size: 0.8rem;
                border: 1px solid rgba(146, 178, 255, 0.32);
                font-weight: 700;
            }

            .voice-stage {
                min-height: 46vh;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                text-align: center;
                gap: 0.56rem;
                position: relative;
                z-index: 1;
            }

            .avatar-orb {
                width: 150px;
                height: 150px;
                border-radius: 50%;
                padding: 6px;
                background: linear-gradient(160deg, rgba(217, 232, 255, 0.85), rgba(104, 149, 242, 0.45));
                box-shadow:
                    0 0 0 10px rgba(106, 165, 255, 0.1),
                    0 18px 45px rgba(5, 15, 34, 0.48);
            }

            .avatar-core {
                width: 100%;
                height: 100%;
                border-radius: 50%;
                background: radial-gradient(70% 70% at 50% 26%, #f4f7ff 0%, #d6e2ff 40%, #a8c1f0 100%);
                display: flex;
                align-items: center;
                justify-content: center;
                color: #305086;
                font-family: 'Space Grotesk', sans-serif;
                font-size: 3.1rem;
                font-weight: 700;
            }

            .avatar-image {
                width: 100%;
                height: 100%;
                border-radius: 50%;
                object-fit: cover;
                object-position: center;
                display: block;
                background: #d7e2f8;
            }

            .voice-status {
                margin: 1rem 0 0;
                font-size: 0.82rem;
                letter-spacing: 0.22em;
                color: var(--text-muted);
                font-weight: 700;
            }

            .voice-substatus {
                margin: 0;
                color: var(--text-muted);
                font-size: 0.84rem;
            }

            .wave-track {
                margin-top: 0.5rem;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 4px;
                min-height: 34px;
            }

            .wave-track span {
                width: 3px;
                border-radius: 99px;
                background: linear-gradient(180deg, rgba(123, 163, 250, 0.92), rgba(52, 99, 184, 0.24));
                animation: wave-idle 1.8s ease-in-out infinite;
                animation-delay: calc(var(--i) * -0.08s);
            }

            .wave-track.active span {
                animation: wave-live 0.85s ease-in-out infinite;
                animation-delay: calc(var(--i) * -0.06s);
            }

            @keyframes wave-idle {
                0%, 100% { height: 6px; opacity: 0.5; }
                50% { height: 16px; opacity: 0.9; }
            }

            @keyframes wave-live {
                0%, 100% { height: 8px; opacity: 0.72; }
                25% { height: 26px; opacity: 1; }
                50% { height: 12px; opacity: 0.85; }
                75% { height: 30px; opacity: 1; }
            }

            .voice-meta-row {
                margin-top: 0.7rem;
                display: flex;
                justify-content: space-between;
                gap: 0.75rem;
                align-items: flex-end;
            }

            .analysis-card {
                max-width: 380px;
                display: flex;
                gap: 0.55rem;
                align-items: flex-start;
                color: var(--text-muted);
            }

            .analysis-dot {
                width: 8px;
                height: 8px;
                border-radius: 50%;
                margin-top: 0.36rem;
                background: var(--ok);
                box-shadow: 0 0 0 6px rgba(95, 166, 255, 0.14);
            }

            .analysis-card h5,
            .duration-card span {
                margin: 0;
                font-size: 0.72rem;
                letter-spacing: 0.13em;
                font-weight: 800;
                color: #6ea4ff;
            }

            .analysis-card p {
                margin: 0.24rem 0 0;
                line-height: 1.36;
                font-size: 0.84rem;
            }

            .duration-card {
                text-align: right;
            }

            .duration-card strong {
                display: block;
                font-family: 'Space Grotesk', sans-serif;
                margin-top: 0.15rem;
                font-size: 2.1rem;
                line-height: 1;
                letter-spacing: 0.01em;
                color: var(--text-main);
            }

            .voice-controls-marker + div[data-testid="stHorizontalBlock"] {
                align-items: center;
                justify-content: center;
                margin: 0.2rem auto 0.45rem;
                max-width: 350px;
            }

            .voice-controls-marker + div[data-testid="stHorizontalBlock"] [data-testid="stButton"] > button {
                min-height: 58px;
                border-radius: 999px;
                border: 1px solid rgba(128, 168, 255, 0.28);
                background: rgba(11, 28, 58, 0.78);
                color: #d6e6ff;
                font-weight: 700;
                transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
            }

            .voice-controls-marker + div[data-testid="stHorizontalBlock"] [data-testid="stButton"] > button:hover {
                transform: translateY(-1px);
                border-color: rgba(132, 188, 255, 0.55);
            }

            .voice-controls-marker + div[data-testid="stHorizontalBlock"] [data-testid="column"]:nth-child(2) [data-testid="stButton"] > button {
                min-height: 96px;
                border-radius: 999px;
                background: linear-gradient(180deg, #69b0ff 0%, #4f94ef 100%);
                color: #f4f8ff;
                border: 1px solid rgba(147, 205, 255, 0.72);
                box-shadow: 0 10px 24px rgba(56, 132, 230, 0.35);
            }

            .voice-controls-marker + div[data-testid="stHorizontalBlock"] [data-testid="column"]:nth-child(1) [data-testid="stButton"] > button,
            .voice-controls-marker + div[data-testid="stHorizontalBlock"] [data-testid="column"]:nth-child(3) [data-testid="stButton"] > button {
                min-height: 58px;
                border-radius: 999px;
            }

            .section-card {
                border: 1px solid var(--stroke);
                border-radius: 16px;
                background: linear-gradient(170deg, rgba(10, 22, 48, 0.74), rgba(8, 15, 35, 0.4));
                box-shadow: 0 14px 28px rgba(5, 14, 30, 0.24);
                padding: 0.95rem 1rem 0.8rem;
                margin-top: 0.8rem;
            }

            .section-card h4 {
                margin: 0;
                font-size: 0.87rem;
                color: #9cc0ff;
                letter-spacing: 0.06em;
            }

            .section-card p {
                margin: 0.25rem 0 0;
                color: var(--text-muted);
                font-size: 0.86rem;
            }

            div[data-testid="stTextArea"] textarea {
                border-radius: 13px;
                border: 1px solid rgba(120, 151, 223, 0.32);
                background: rgba(6, 16, 35, 0.72);
                color: var(--text-main);
                font-size: 0.96rem;
                line-height: 1.52;
                min-height: 120px;
            }

            div[data-testid="stTextArea"] textarea:focus {
                border-color: rgba(128, 182, 255, 0.72);
                box-shadow: 0 0 0 1px rgba(128, 182, 255, 0.36);
            }

            .voice-send-marker + div[data-testid="stHorizontalBlock"] [data-testid="stButton"] > button {
                border-radius: 12px;
                min-height: 48px;
                background: rgba(14, 34, 68, 0.86);
                border: 1px solid rgba(131, 171, 247, 0.34);
                color: #d8e7ff;
                font-weight: 700;
            }

            .voice-send-marker + div[data-testid="stHorizontalBlock"] [data-testid="column"]:first-child [data-testid="stButton"] > button {
                background: linear-gradient(180deg, #4f95f4 0%, #3a7fdf 100%);
                border-color: rgba(150, 201, 255, 0.6);
            }

            .voice-end-marker + div[data-testid="stHorizontalBlock"] [data-testid="stButton"] > button {
                border-radius: 13px;
                min-height: 50px;
                background: linear-gradient(180deg, var(--danger) 0%, var(--danger-soft) 100%);
                border: 1px solid rgba(255, 189, 195, 0.5);
                color: #fff4f5;
                font-weight: 800;
                box-shadow: 0 10px 24px rgba(207, 62, 75, 0.32);
            }

            .voice-end-marker + div[data-testid="stHorizontalBlock"] {
                max-width: 360px;
                margin: 0.35rem auto 0;
            }

            .empty-state {
                border: 1px dashed rgba(131, 166, 241, 0.42);
                border-radius: 12px;
                padding: 0.75rem 0.86rem;
                color: var(--text-muted);
                font-size: 0.87rem;
                margin: 0.55rem 0 0.2rem;
                background: rgba(7, 22, 50, 0.36);
            }

            [data-testid="stExpander"] {
                border-radius: 13px;
                border: 1px solid var(--stroke);
                background: rgba(8, 18, 38, 0.52);
            }

            [data-testid="stMetric"] {
                border-radius: 12px;
                border: 1px solid rgba(135, 169, 241, 0.24);
                background: rgba(12, 27, 57, 0.56);
                box-shadow: 0 8px 20px rgba(2, 10, 24, 0.22);
                padding: 0.2rem 0.5rem;
            }

            [data-testid="stToast"] {
                border-radius: 12px;
                border: 1px solid rgba(133, 182, 255, 0.38);
                background: rgba(8, 23, 51, 0.96);
                color: #e8f2ff;
            }

            .summary-shell {
                border: 1px solid var(--stroke);
                border-radius: 18px;
                padding: 1rem;
                background: linear-gradient(165deg, rgba(10, 23, 48, 0.8), rgba(8, 16, 34, 0.4));
                box-shadow: 0 16px 34px rgba(1, 8, 23, 0.34);
                margin-top: 0.2rem;
            }

            .summary-shell h2 {
                margin: 0;
                color: #dceaff;
                font-size: 1.45rem;
                letter-spacing: 0.01em;
                font-family: 'Space Grotesk', sans-serif;
            }

            .summary-shell p {
                color: var(--text-muted);
                margin: 0.35rem 0 0;
            }

            div[data-testid="stAlert"] {
                border-radius: 13px;
            }

            div[data-testid="stSidebar"] {
                border-left: 1px solid rgba(139, 178, 255, 0.22);
                background: linear-gradient(180deg, rgba(7, 19, 42, 0.92), rgba(4, 12, 28, 0.98));
            }

            audio {
                display: none;
            }

            @media (max-width: 900px) {
                .voice-shell {
                    min-height: 70vh;
                    padding: 0.9rem 0.82rem 0.95rem;
                }

                .voice-meta-row {
                    flex-direction: column;
                    align-items: flex-start;
                    gap: 0.8rem;
                }

                .duration-card {
                    text-align: left;
                }

                .duration-card strong {
                    font-size: 1.75rem;
                }
            }
        </style>
        """,
    )


@st.cache_resource
def load_emotion_engine() -> EmotionEngine:
    return EmotionEngine("models/emotion_engine/final")


@st.cache_resource
def load_tts_engine() -> TTSEngine:
    engine = TTSEngine()
    apply_mood(engine, "warm")
    return engine


@st.cache_data
def load_avatar_data_uri() -> str:
    candidates = [
        Path(r"C:\Users\Victus\Desktop\karunaAIRestore\img\avatar.jpeg"),
        Path("img/avatar.jpeg"),
        Path("img/avatar.jpg"),
        Path("img/avatar.png"),
    ]

    mime_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }

    for avatar_path in candidates:
        if avatar_path.exists() and avatar_path.is_file():
            encoded = base64.b64encode(avatar_path.read_bytes()).decode("ascii")
            mime_type = mime_map.get(avatar_path.suffix.lower(), "image/png")
            return f"data:{mime_type};base64,{encoded}"

    return ""


def init_state() -> None:
    if "emotion_engine" not in st.session_state:
        with st.spinner("Memuat engine emosi..."):
            st.session_state.emotion_engine = load_emotion_engine()

    if "tts_engine" not in st.session_state:
        with st.spinner("Memuat engine suara..."):
            st.session_state.tts_engine = load_tts_engine()

    if "orch" not in st.session_state:
        st.session_state.orch = KarunaOrchestrator(st.session_state.emotion_engine)
    if "referral_decision" not in st.session_state:
        st.session_state.referral_decision = None
    if "is_recording" not in st.session_state:
        st.session_state.is_recording = False
    if "recorder" not in st.session_state:
        st.session_state.recorder = AudioRecorder()
    if "auto_tts" not in st.session_state:
        st.session_state.auto_tts = True
    if "pending_audio" not in st.session_state:
        st.session_state.pending_audio = None
    if "last_audio" not in st.session_state:
        st.session_state.last_audio = None
    if "welcome_played" not in st.session_state:
        st.session_state.welcome_played = False
    if "session_started_at" not in st.session_state:
        st.session_state.session_started_at = time.time()
    if "last_transcript" not in st.session_state:
        st.session_state.last_transcript = ""
    if "manual_text" not in st.session_state:
        st.session_state.manual_text = ""


def reset_to_new_session() -> None:
    st.session_state.orch = KarunaOrchestrator(st.session_state.emotion_engine)
    st.session_state.referral_decision = None
    st.session_state.is_recording = False
    st.session_state.recorder = AudioRecorder()
    st.session_state.pending_audio = None
    st.session_state.last_audio = None
    st.session_state.welcome_played = False
    st.session_state.session_started_at = time.time()
    st.session_state.last_transcript = ""
    st.session_state.manual_text = ""


def format_duration(total_seconds: int) -> str:
    mins, secs = divmod(total_seconds, 60)
    hours, mins = divmod(mins, 60)
    if hours > 0:
        return f"{hours:02d}:{mins:02d}:{secs:02d}"
    return f"{mins:02d}:{secs:02d}"


def get_voice_status_text() -> tuple[str, str]:
    if st.session_state.is_recording:
        return (
            "MENDENGARKAN SUARA ANDA",
            "Berbicara natural. Tekan kontrol utama untuk mengirim.",
        )
    return (
        "MENUNGGU SUARA ANDA",
        "Gunakan kontrol utama untuk memulai rekaman suara.",
    )


def get_analysis_copy(orch: KarunaOrchestrator) -> str:
    if not orch.last_cds_result:
        return "Analyzing vocal tonality untuk mengoptimalkan respons empatik dan mindfulness guidance."

    level_to_copy = {
        "NORMAL": "Sinyal distress tetap rendah. Karuna menjaga percakapan suportif dan stabil.",
        "L1": "Ada sinyal tekanan ringan. Karuna menyesuaikan tone agar lebih menenangkan.",
        "L2": "Terlihat tekanan berat. Sistem meningkatkan kewaspadaan dan respons pendampingan.",
        "L3": "Sinyal krisis tinggi terdeteksi. Prioritas diarahkan ke keamanan dan dukungan cepat.",
    }
    return level_to_copy.get(orch.last_cds_result.level, level_to_copy["NORMAL"])


def generate_tts_bytes(text: str, orch: KarunaOrchestrator) -> bytes:
    tts_engine = st.session_state.tts_engine
    cds_result = orch.last_cds_result

    if cds_result:
        if cds_result.level == "L3":
            apply_mood(tts_engine, "gentle")
        elif cds_result.level == "L2":
            apply_mood(tts_engine, "concerned")
        else:
            apply_mood(tts_engine, "warm")
    else:
        apply_mood(tts_engine, "warm")

    return tts_engine.synthesize(text)


def play_pending_audio() -> None:
    if st.session_state.pending_audio and st.session_state.auto_tts:
        audio_bytes = st.session_state.pending_audio
        st.session_state.pending_audio = None
        st.session_state.last_audio = audio_bytes
        st.audio(audio_bytes, format="audio/mp3", autoplay=True)


def maybe_queue_welcome_audio(orch: KarunaOrchestrator) -> None:
    if orch.msg_count > 0:
        return

    if not st.session_state.auto_tts or st.session_state.welcome_played:
        return

    try:
        welcome_audio = generate_tts_bytes(WELCOME_MESSAGE, orch)
        st.session_state.pending_audio = welcome_audio
        st.session_state.welcome_played = True
        st.rerun()
    except Exception as exc:
        st.session_state.welcome_played = True
        st.caption(f"TTS welcome tidak tersedia: {exc}")


def render_voice_shell(orch: KarunaOrchestrator) -> None:
    elapsed_seconds = int(time.time() - st.session_state.session_started_at)
    duration_text = format_duration(max(elapsed_seconds, 0))
    status_headline, status_subline = get_voice_status_text()
    analysis_copy = get_analysis_copy(orch)
    avatar_uri = load_avatar_data_uri()

    bars = "".join(f"<span style='--i:{idx};'></span>" for idx in range(1, 18))
    wave_class = "active" if st.session_state.is_recording else "idle"

    if avatar_uri:
        avatar_markup = f'<img class="avatar-image" src="{avatar_uri}" alt="Karuna avatar" loading="eager"/>'
    else:
        avatar_markup = '<div class="avatar-core" aria-hidden="true">K</div>'

    html = (
        f'<section class="voice-shell">'
        f'<div class="voice-topbar">'
        f'<div class="brand-group">'
        f'<span class="icon-chip" aria-hidden="true">'
        f'<svg width="15" height="15" viewBox="0 0 24 24" fill="none">'
        f'<path d="M4 7h16M4 12h16M4 17h16" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"/>'
        f'</svg></span>'
        f'<span class="brand-text">Karuna.ai</span>'
        f'</div>'
        f'<div class="action-group">'
        f'<a class="action-link" href="#" aria-label="Support">Support</a>'
        f'<a class="action-link" href="#" aria-label="About">About Us</a>'
        f'<span class="profile-dot" aria-hidden="true">K</span>'
        f'</div>'
        f'</div>'
        f'<div class="voice-stage">'
        f'<div class="avatar-orb">{avatar_markup}</div>'
        f'<p class="voice-status">{status_headline}</p>'
        f'<p class="voice-substatus">{status_subline}</p>'
        f'<div class="wave-track {wave_class}" aria-hidden="true">{bars}</div>'
        f'</div>'
        f'<div class="voice-meta-row">'
        f'<div class="analysis-card">'
        f'<span class="analysis-dot" aria-hidden="true"></span>'
        f'<div><h5>ACTIVE ANALYSIS</h5><p>{analysis_copy}</p></div>'
        f'</div>'
        f'<div class="duration-card">'
        f'<span>SESSION DURATION</span>'
        f'<strong>{duration_text}</strong>'
        f'</div>'
        f'</div>'
        f'</section>'
    )
    st.markdown(html, unsafe_allow_html=True)


def process_user_turn(user_input: str, orch: KarunaOrchestrator) -> bool:
    cleaned_input = user_input.strip()
    if not cleaned_input:
        st.warning("Input kosong. Coba rekam ulang atau ketik pesan.")
        return False

    st.session_state.last_transcript = cleaned_input

    with st.spinner("Karuna sedang menganalisis dan menyiapkan respons..."):
        result = orch.process(cleaned_input)

    if st.session_state.auto_tts:
        try:
            st.session_state.pending_audio = generate_tts_bytes(result.ai_response, orch)
        except Exception as exc:
            st.caption(f"TTS tidak tersedia: {exc}")

    st.toast("Respons Karuna siap.", icon=":material/check_circle:")
    return True


def handle_record_control(orch: KarunaOrchestrator) -> None:
    recorder = st.session_state.recorder

    if not st.session_state.is_recording:
        try:
            recorder.start()
            st.session_state.is_recording = True
            st.toast("Rekaman dimulai.", icon=":material/mic:")
            st.rerun()
        except Exception as exc:
            st.error(f"Gagal mulai rekaman: {exc}")
        return

    st.session_state.is_recording = False

    try:
        recorder.stop()
    except Exception as exc:
        st.error(f"Gagal menghentikan rekaman: {exc}")
        st.rerun()
        return

    audio_bytes = recorder.get_wav_bytes()
    duration = recorder.get_duration()

    if duration < 0.6:
        st.warning("Rekaman terlalu pendek. Coba lagi.")
        st.rerun()
        return

    with st.spinner("Mentranskripsi suara..."):
        transcript = transcribe_audio(audio_bytes)

    if not transcript:
        st.error("Suara belum terbaca dengan jelas. Silakan coba lagi.")
        st.rerun()
        return

    st.toast("Transkripsi berhasil.", icon=":material/translate:")
    if process_user_turn(transcript, orch):
        st.rerun()


def render_control_cluster(orch: KarunaOrchestrator) -> None:
    render_html('<div class="voice-controls-marker"></div>')
    col_left, col_center, col_right = st.columns([1.05, 1.25, 1.05], gap="small")

    with col_left:
        replay_clicked = st.button(
            "Replay",
            key="btn_replay",
            use_container_width=True,
            help="Putar ulang respons suara terakhir.",
        )

    with col_center:
        center_label = "Stop & Send" if st.session_state.is_recording else "Start Listening"
        record_clicked = st.button(
            center_label,
            key="btn_record_toggle",
            type="primary",
            use_container_width=True,
            help="Mulai atau akhiri rekaman suara.",
        )

    with col_right:
        clear_clicked = st.button(
            "Clear Draft",
            key="btn_clear_draft",
            use_container_width=True,
            help="Kosongkan draft input teks.",
        )

    if replay_clicked:
        if st.session_state.last_audio:
            st.session_state.pending_audio = st.session_state.last_audio
            st.toast("Memutar ulang respons terakhir.", icon=":material/play_circle:")
            st.rerun()
        else:
            st.info("Belum ada audio respons untuk diputar ulang.")

    if clear_clicked:
        st.session_state.manual_text = ""
        st.toast("Draft dibersihkan.", icon=":material/backspace:")
        st.rerun()

    if record_clicked:
        handle_record_control(orch)


def render_crisis_banner(orch: KarunaOrchestrator) -> None:
    if not orch.last_cds_result:
        return

    if orch.last_cds_result.level == "L3":
        st.error(HELP_LINE_MESSAGE)
    elif orch.last_cds_result.level == "L2":
        st.warning("Karuna melihat tekanan cukup berat. Karuna tetap di sini menemani kamu.")


def render_end_session_action(orch: KarunaOrchestrator) -> None:
    if orch.msg_count == 0:
        st.caption("Session summary akan aktif setelah ada percakapan.")
        return

    render_html('<div class="voice-end-marker"></div>')
    mid_col = st.columns([1, 1.1, 1], gap="small")[1]
    with mid_col:
        if st.button("End Session", key="btn_end_session", type="primary", use_container_width=True):
            with st.spinner("Merangkum sesi..."):
                orch.end_session()
            st.toast("Ringkasan sesi selesai dibuat.", icon=":material/summarize:")
            st.rerun()


def render_summary_page(orch: KarunaOrchestrator) -> None:
    summary = orch.summary
    if summary is None:
        st.error("Ringkasan sesi belum tersedia. Coba akhiri sesi lagi.")
        return

    st.markdown(
        '<div class="summary-shell"><h2>Session Summary</h2>'
        '<p>Ringkasan ini disusun dari pola emosi, sinyal krisis, dan konteks percakapan sesi terakhir.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    flag_config = {
        "LOW": ("Risiko Rendah", "info"),
        "MEDIUM": ("Perlu Perhatian", "warning"),
        "HIGH": ("Risiko Tinggi", "error"),
    }
    flag_label, widget_kind = flag_config.get(summary.flag, (summary.flag, "info"))

    col_flag, col_trend, col_total = st.columns(3)
    with col_flag:
        getattr(st, widget_kind)(f"**{flag_label}**\n\n{summary.flag_reasoning}")
    with col_trend:
        st.metric("Tren distress", summary.tren_distress)
    with col_total:
        st.metric("Jumlah pesan", summary.jumlah_pesan)

    tab_notes, tab_tech = st.tabs(["Catatan Naratif", "Detail Teknis"])

    with tab_notes:
        st.markdown(summary.paragraf)
        st.success(summary.pesan_penutup)

    with tab_tech:
        st.write(f"CDS level akhir: {summary.cds_level_akhir}")
        st.write(f"Distress awal: {summary.distress_awal:.1%}")
        st.write(f"Distress akhir: {summary.distress_akhir:.1%}")

    st.markdown("---")
    referral = st.session_state.referral_decision

    if referral is None:
        st.subheader("Lanjutkan ke profesional?")
        c_yes, c_no = st.columns(2)
        with c_yes:
            if st.button("Ya, teruskan ke psikolog", key="summary_ref_yes", type="primary", use_container_width=True):
                st.session_state.referral_decision = "yes"
                st.toast("Data sesi disimpan untuk referral.", icon=":material/check:")
                st.rerun()
        with c_no:
            if st.button("Tidak, hapus data saya", key="summary_ref_no", use_container_width=True):
                if summary.session_file:
                    delete_session_json(summary.session_file)
                st.session_state.referral_decision = "no"
                st.toast("Data sesi dihapus permanen.", icon=":material/delete:")
                st.rerun()
    elif referral == "yes":
        st.success(f"Catatan sesi disimpan. Session ID: {summary.session_id}")
    else:
        st.info("Data sesi sudah dihapus.")

    if st.button("Mulai sesi baru", key="summary_new_session", type="primary", use_container_width=True):
        reset_to_new_session()
        st.rerun()


def render_sidebar(orch: KarunaOrchestrator) -> None:
    with st.sidebar:
        st.subheader("Voice Settings")
        st.session_state.auto_tts = st.toggle("Auto-play respons suara", value=st.session_state.auto_tts)
        st.caption("Jika nonaktif, respons suara tidak diputar otomatis.")

        st.markdown("---")
        st.subheader("Session Debug")
        st.metric("Pesan", orch.msg_count)
        st.metric("Recording", "ON" if st.session_state.is_recording else "OFF")

        if orch.last_cds_result:
            st.metric("CDS", orch.last_cds_result.level)
            st.caption(f"Score: {orch.last_cds_result.score:.3f}")

        if orch.emotion_history:
            latest_emotion = orch.emotion_history[-1]
            st.metric("Emosi dominan", latest_emotion.dominant)
            st.caption(f"Distress: {latest_emotion.distress_score:.1%}")


def main() -> None:
    configure_page()
    inject_styles()
    init_state()

    orch = st.session_state.orch

    play_pending_audio()

    if orch.session_ended and orch.summary:
        render_summary_page(orch)
        render_sidebar(orch)
        return

    maybe_queue_welcome_audio(orch)

    render_voice_shell(orch)
    render_control_cluster(orch)
    render_crisis_banner(orch)
    render_end_session_action(orch)
    render_sidebar(orch)


if __name__ == "__main__":
    main()