import os
os.environ["USE_TF"] = "0"
os.environ["USE_TORCH"] = "1"

import streamlit as st
from s1_conversational.prompt_builder   import build_system_prompt
from s1_conversational.groq_client      import chat_with_groq
from s1_conversational.output_validator import validate
from s2_emotion.emotion_engine          import EmotionEngine
from s3_crisis.cds_engine              import analyze_crisis
from pipeline.orchestrator             import KarunaOrchestrator
from s4_summary.summary_generator      import delete_session_json

# ── 1. Configuration & Styling ────────────────────────────────────────────
def setup_page():
    st.set_page_config(
        page_title="KarunaAI | Mindful Companion",
        page_icon="🌱",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Modern SaaS Dashboard CSS injected into Streamlit
    custom_css = """
    <style>
        /* Modern Typography */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        /* Apply Inter font */
        html, body, [class*="css"], .stMarkdown {
            font-family: 'Inter', sans-serif !important;
        }

        /* Container Styling for rounded corners & shadow */
        [data-testid="stChatMessage"] {
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
            border: 1px solid rgba(200,200,200,0.15);
        }
        
        /* Metric Box Styling */
        [data-testid="stMetric"] {
            background-color: var(--secondary-background-color);
            padding: 15px 20px;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border: 1px solid rgba(200,200,200,0.1);
        }
        
        /* Buttons Styling (SaaS feel) */
        .stButton>button {
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        .stButton>button:hover {
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transform: translateY(-1px);
        }

        /* Headers crispness */
        h1, h2, h3 {
            font-weight: 600;
            letter-spacing: -0.02em;
        }
        
        /* Toast notification tweaks */
        [data-testid="stToast"] {
            border-radius: 8px;
            font-family: 'Inter', sans-serif;
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

# ── 2. Business Logic / State Management ──────────────────────────────────
@st.cache_resource
def load_emotion_engine():
    return EmotionEngine("models/emotion_engine/final")

def init_state():
    if "emotion_engine" not in st.session_state:
        with st.spinner("Initializing Emotion Engine..."):
            st.session_state.emotion_engine = load_emotion_engine()
            
    if "orch" not in st.session_state:
        st.session_state.orch = KarunaOrchestrator(st.session_state.emotion_engine)
        
    if "referral_decision" not in st.session_state:
        st.session_state.referral_decision = None

# ── 3. Modular UI Components ──────────────────────────────────────────────

def render_sidebar(orch):
    with st.sidebar:
        st.title("🌱 KarunaAI Ops")
        st.caption("Diagnostic & Control Panel")
        
        st.divider()
        
        st.subheader("Session Control")
        if orch.msg_count > 0:
            if st.button("End Session & Summarize", type="primary", use_container_width=True):
                with st.status("Summarizing session...", expanded=True) as status:
                    st.write("Analyzing distress levels...")
                    st.write("Generating professional summary...")
                    orch.end_session()
                    status.update(label="Summary complete!", state="complete")
                st.rerun()
        else:
            st.info("Awaiting user input to begin session tracking.", icon="💡")

        st.divider()
        
        st.subheader("Real-time Telemetry")
        st.metric("Interaction Count", orch.msg_count)
        
        cds_result = orch.last_cds_result
        if not cds_result:
            st.caption("Telemetry will populate after the first message.")
        else:
            cds = cds_result
            d = cds.detail
            
            with st.expander("Crisis Detection (S3)", expanded=False):
                level_badge = {"NORMAL": "✅ [OK]", "L1": "⚠️ [L1]", "L2": "🟠 [L2]", "L3": "🚨 [L3]"}
                st.write(f"**Level:** {level_badge.get(cds.level, '[-]')} {cds.level}")
                st.write(f"**Score:** `{cds.score:.4f}`")
                st.write(f"**Triggers:** `{', '.join(cds.triggers)}`")
                
                # Further layer details inside
                st.markdown("**Layer 1 — Keyword**")
                if d.get("l2_skipped"):
                    st.write("L3 keyword eksplisit — L2 & L3 di-skip")
                else:
                    st.write(f"`{d['l1_level']}` conf=`{d['l1_conf']:.2f}` skor=`{d.get('score_l1', 0):.4f}`")
                    
                st.markdown("**Layer 2 — IndoBERT**")
                if d.get("l2_skipped"):
                    st.write("*Skipped*")
                else:
                    st.write(f"`{d['l2_label']}` -> `{d['l2_level']}` conf=`{d['l2_conf']:.4f}` skor=`{d.get('score_l2', 0):.4f}`")
                
                st.markdown("**Layer 3 — History Trend**")
                if d.get("l3_skipped"):
                    st.write("*Skipped*")
                else:
                    st.write(f"Skor L3=`{d.get('l3_score', 0):.4f}` kontribusi=`{d.get('score_l3', 0):.4f}`")

            if orch.emotion_history:
                with st.expander("Emotion Engine (S2)", expanded=False):
                    er = orch.emotion_history[-1]
                    st.write(f"**Dominant:** {er.dominant} ({er.score:.1%})")
                    st.write(f"**Topics:** {', '.join(er.topics)}")
                    st.write(f"**Distress:** `{er.distress_score:.1%}`")
                    
                    dist_sorted = sorted(er.distribution.items(), key=lambda x: x[1], reverse=True)
                    st.bar_chart({e: [v] for e, v in dist_sorted}, height=130)

        st.divider()
        st.metric(
            "Model Validator",
            "OK" if orch.last_valid else f"WARN: {orch.last_reason}"
        )


def render_summary_dashboard(orch):
    s = orch.summary

    st.header("📑 Session Overview")
    st.markdown("Assess the synthesized metrics and narrative of the completed session.")
    
    # Flag Config Mapping
    FLAG_CONFIG = {
        "LOW"   : ("Low Risk / Risiko Rendah",   "normal", "✅"),
        "MEDIUM": ("Monitor / Perlu Perhatian", "warning", "⚠️"),
        "HIGH"  : ("High Risk / Risiko Tinggi",     "error", "🚨"),
    }
    label, delta_color, icon = FLAG_CONFIG.get(s.flag, (s.flag, "off", "ℹ️"))
    
    # ── Top Row Metrics ───────────────────────────────────────────────────
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Risk Status", f"{icon} {label}", delta=s.flag_reasoning, delta_color=delta_color)
    with m2:
        tren_icon = {"membaik": "↗️", "memburuk": "↘️", "stabil": "➡️"}
        st.metric("Distress Trend", f"{s.tren_distress.capitalize()}", f"{tren_icon.get(s.tren_distress, '')}")
    with m3:
        st.metric("Total Messages", s.jumlah_pesan)

    st.markdown("---")
    
    # ── Narrative & Technical Details via Tabs ────────────────────────────
    tab1, tab2 = st.tabs(["📝 Narrative Notes", "📊 Technical Insights"])
    
    with tab1:
        st.markdown("### Clinical Session Notes")
        st.info(s.paragraf)
        
        st.markdown("### Closing Remarks Delivered")
        st.success(s.pesan_penutup)
        
    with tab2:
        st.markdown("### End-of-Session Telemetry Tracker")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.write(f"- **Final CDS Level:** `{s.cds_level_akhir}`")
            st.write(f"- **Initial Distress Score:** `{s.distress_awal:.1%}`")
        with col_c2:
            st.write(f"- **Final Distress Score:** `{s.distress_akhir:.1%}`")

    # ── Referral to Psychologist ──────────────────────────────────────────
    st.markdown("---")
    referral = st.session_state.referral_decision
    
    if referral is None:
        st.subheader("Post-Session Action")
        st.caption(
            "Karuna has temporarily cached this session's telemetry. "
            "You may forward this to a human professional, or permanently erase the trace."
        )
        
        col_yes, col_no = st.columns(2)
        with col_yes:
            if st.button("Forward to Psychologist", type="primary", use_container_width=True):
                st.session_state.referral_decision = "yes"
                st.toast("Referral package created and persisted.", icon="📁")
                st.rerun()
        with col_no:
            if st.button("Permanent Erase", type="secondary", use_container_width=True):
                if s.session_file:
                    delete_session_json(s.session_file)
                st.session_state.referral_decision = "no"
                st.toast("Session data permanently destroyed.", icon="🗑️")
                st.rerun()
                
    elif referral == "yes":
        st.success(f"**Referral Preserved.** A psychological professional can access this using Session ID: `{s.session_id}`")
        with st.expander("View Retained Payload Dump"):
            st.json({
                "session_id"    : s.session_id,
                "flag"          : s.flag,
                "tren_distress" : s.tren_distress,
                "jumlah_pesan"  : s.jumlah_pesan,
                "ringkasan"     : s.paragraf,
            })
            
    elif referral == "no":
        st.info("**Session Purged.** No telemetry or records remain.")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Start New Session", type="primary", use_container_width=True):
        st.session_state.orch = KarunaOrchestrator(st.session_state.emotion_engine)
        st.session_state.referral_decision = None
        st.rerun()
        
    st.stop()


def render_chat_interface(orch):
    WELCOME_MESSAGE = (
        "Halo, aku Karuna. Aku di sini buat dengerin kamu. "
        "Kalau kamu nyaman, kamu bisa mulai cerita pelan-pelan dari hal yang paling berat sekarang."
    )
    
    st.title("KarunaAI — Listener Module")
    st.caption("Active Deep Listening Protocol (S1 / S2 / S3 L1+L2+L3 / S4)")
    
    # Create the main chat container to hold the history
    chat_container = st.container()
    
    with chat_container:
        # Greetings on load
        if orch.msg_count == 0:
            with st.chat_message("assistant"):
                st.write(WELCOME_MESSAGE)
                
        # History iterator
        for msg in orch.chat_log:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                
    # Input Bar pinned to the bottom 
    if user_input := st.chat_input("Ceritakan apa yang kamu rasakan..."):
        with st.chat_message("user"):
            st.write(user_input)
            
        with st.spinner("Karuna is analyzing and formulating a response..."):
            result = orch.process(user_input)
            
        # Crisis Banner Injection
        if result.crisis_banner == "L3":
            st.error(
                "**Karuna mendeteksi kamu sedang dalam kondisi yang sangat berat.**\n\n"
                "Kamu tidak sendirian. Jika kamu membutuhkan bantuan segera, "
                "hubungi **Into The Light Indonesia: 119 ext 8** (24 jam, gratis).",
                icon="🚨"
            )
        elif result.crisis_banner == "L2":
            st.warning(
                "Karuna memperhatikan kamu sedang mengalami tekanan yang berat. Karuna di sini bersamamu.",
                icon="⚠️"
            )
            
        with st.chat_message("assistant"):
            st.write(result.ai_response)
            if not result.is_valid:
                st.caption(f"Validator notes: {result.validator_note}")

# ── 4. Main Application ───────────────────────────────────────────────────

def main():
    # 1. Setup layout & config
    setup_page()
    
    # 2. Init resources & state engines
    init_state()
    
    orch = st.session_state.orch
    
    # 3. Route Views logically
    if orch.session_ended and orch.summary:
        # When ended, show the summary dashboard mode exclusively
        render_summary_dashboard(orch)
    else:
        # While active, side panel for debug/telemetry, center for chats
        render_sidebar(orch)
        render_chat_interface(orch)

if __name__ == "__main__":
    main()
