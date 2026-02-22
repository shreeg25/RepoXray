import streamlit as st
import os
import sys
from streamlit.runtime.scriptrunner import get_script_run_ctx
from dotenv import load_dotenv, find_dotenv

# 1. Force find and load .env from anywhere in the project tree
load_dotenv(find_dotenv(), override=True)

# --- FIX FOR "NoSessionContext" THREADING ERRORS ---
class StreamlitRedirect:
    def __init__(self, st_empty_block):
        self.st_empty_block = st_empty_block
        self.buffer = []

    def write(self, msg):
        if msg.strip():
            self.buffer.append(msg.strip())
            # ONLY update UI if called from the main Streamlit thread
            if get_script_run_ctx() is not None:
                display_text = "\n".join(self.buffer[-15:])
                self.st_empty_block.code(display_text, language="bash")

    def flush(self):
        pass
# ----------------------------------------------------------------

# Page config
st.set_page_config(page_title="RepoXray | Terminal", page_icon="💻", layout="wide", initial_sidebar_state="expanded")

# --- CYBERPUNK THEME CSS INJECTION ---
st.markdown("""
<style>
/* Base Dark Theme & Grid */
.stApp {
    background-color: #050505;
    background-image: 
        linear-gradient(rgba(0, 255, 234, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 255, 234, 0.03) 1px, transparent 1px);
    background-size: 30px 30px;
    color: #ffffff;
    font-family: 'Courier New', Courier, monospace;
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background-color: #08080a !important;
    border-right: 2px solid #ff00ff;
}
.sidebar-title {
    color: #00ffea;
    font-weight: 900;
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
    text-shadow: 0 0 5px rgba(0,255,234,0.5);
}
.sidebar-subtitle {
    color: #4a5568;
    font-size: 0.8rem;
    background-color: #1a202c;
    padding: 4px;
    border-radius: 2px;
    margin-bottom: 2rem;
}
.sys-badge {
    color: #00ff41;
    font-size: 0.8rem;
    background-color: #002200;
    padding: 4px 8px;
    border: 1px solid #00ff41;
    margin-bottom: 10px;
    display: inline-block;
}

/* Main Headers & Accents */
.main-title {
    color: #00ffea !important;
    font-weight: 900;
    letter-spacing: 2px;
    text-shadow: 0 0 8px rgba(0,255,234,0.6);
    margin-bottom: 5px;
}
.magenta-line {
    height: 2px;
    background-color: #ff00ff;
    width: 100%;
    margin-bottom: 15px;
    box-shadow: 0 0 10px #ff00ff;
}
.sub-title {
    color: #ff00ff;
    font-size: 1.1rem;
    font-weight: bold;
    margin-bottom: 30px;
}
.dataset-title {
    color: #ff00ff;
    font-size: 1.5rem;
    font-weight: bold;
    margin-top: 40px;
    margin-bottom: 10px;
}

/* Inputs styling */
.stTextInput>div>div>input {
    background-color: transparent !important;
    color: #00ffea !important;
    border: none !important;
    border-bottom: 2px solid #00ffea !important;
    border-radius: 0 !important;
    font-family: 'Courier New', Courier, monospace !important;
    box-shadow: none !important;
}
.stTextInput>div>div>input:focus {
    border-bottom: 2px solid #ff00ff !important;
    box-shadow: 0 5px 5px -5px #ff00ff !important;
}

/* Buttons */
.stButton>button {
    background-color: transparent !important;
    color: #00ffea !important;
    border: 1px solid #00ffea !important;
    box-shadow: 0 0 5px rgba(0,255,234,0.2) !important;
    text-transform: uppercase !important;
    font-weight: bold !important;
    letter-spacing: 1px !important;
    transition: all 0.3s ease !important;
    border-radius: 2px !important;
}
.stButton>button:hover {
    background-color: #00ffea !important;
    color: #000 !important;
    box-shadow: 0 0 15px #00ffea !important;
}

/* System Logs / Success Box */
[data-testid="stAlert"] {
    background-color: #002200 !important;
    border: 1px solid #00ff41 !important;
    color: #00ff41 !important;
    border-radius: 4px;
}
[data-testid="stAlert"] * {
    color: #00ff41 !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
    border-bottom: 1px solid #333;
}
.stTabs [data-baseweb="tab"] {
    color: #555 !important;
    font-family: 'Courier New', Courier, monospace;
    font-weight: bold;
    font-size: 1rem;
    background-color: transparent;
    border: none;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: #00ffea !important;
    border-bottom: 3px solid #00ffea !important;
}
</style>
""", unsafe_allow_html=True)
# -------------------------------------

# --- SIDEBAR: TERMINAL ACCESS ---
with st.sidebar:
    st.markdown("<div class='sidebar-title'>TERMINAL_ACCESS</div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-subtitle'>AWAITING CONFIGURATION PARAMS...</div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    target_dir = st.text_input("TARGET_DIR [PATH]", value=".")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Pre-fill placeholder if the key is already found in the .env file
    env_key_exists = bool(os.environ.get("GOOGLE_API_KEY"))
    placeholder_text = "******** (Loaded from .env)" if env_key_exists else "Enter your API Key..."
    api_key_input = st.text_input("AUTH_TOKEN [API_KEY]", type="password", placeholder=placeholder_text)
    
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<div class='sys-badge'>&lt;SYS_ID: EPOCH_X_NASIKO&gt;</div>", unsafe_allow_html=True)
    st.markdown("<div class='sys-badge'>&lt;STATUS: ONLINE&gt;</div>", unsafe_allow_html=True)


# --- MAIN ORCHESTRATOR ---
st.markdown("<div class='main-title'>REPO_XRAY // ORCHESTRATOR</div>", unsafe_allow_html=True)
st.markdown("<div class='magenta-line'></div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>&gt;&gt; NEURAL NETWORK CODEBASE ANALYSIS ENGAGED</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Centered Generation Button
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    start_scan = st.button("GENERATE README & SECURITY AUDIT", use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

if start_scan:
    # 1. Update environment if the user manually typed an API key
    if api_key_input.strip():
        os.environ["GOOGLE_API_KEY"] = api_key_input.strip()

    # 2. Strict Pre-flight Check: Catch missing keys or dummy text
    current_key = os.environ.get("GOOGLE_API_KEY", "").strip()
    dummy_keys = ["", "your_api_key_here", "insert_key_here", "<your_api_key>"]
    
    if not current_key or current_key.lower() in dummy_keys:
        st.error("❌ ERR_AUTH_FAILURE: GOOGLE_API_KEY is missing or invalid. Please type it in the sidebar.")
        st.stop() 

    target_dir_abs = os.path.abspath(target_dir)
    
    # 3. Pre-flight Check: Ensure Directory Exists
    if not os.path.exists(target_dir_abs):
        st.error(f"❌ ERR_DIR_NOT_FOUND: Path does not exist -> {target_dir_abs}")
        st.stop()
        
    # UI Elements for terminal logs
    log_expander = st.expander(">> LIVE_TERMINAL_LOGS... (Extracting Context)", expanded=True)
    log_container = log_expander.empty()
    
    # Intercept print statements safely
    old_stdout = sys.stdout
    sys.stdout = StreamlitRedirect(log_container)
    
    try:
        with st.spinner("BREACHING_MAINFRAME & INITIATING DEEP SCAN... [EST. TIME: 1-3 MINS] ⏳"):
            
            # DELAYED IMPORT
            try:
                from src.agents import ReadmeAgent
            except ImportError:
                try:
                    from app.agents import ReadmeAgent
                except ImportError:
                    from agents import ReadmeAgent
                    
            agent = ReadmeAgent(target_dir=target_dir_abs)
            readme_content = agent.generate() 
            
        st.success("✓ PROTOCOL COMPLETE // NEURAL SCAN FINISHED")
        
        # --- FIX FOR EMPTY PAYLOAD / AGENT AUTO-SAVE ---
        readme_path = os.path.join(target_dir_abs, "README.md")
        
        # If the agent returned nothing, check if it saved the file to disk directly
        if not readme_content and os.path.exists(readme_path):
            with open(readme_path, "r", encoding="utf-8") as f:
                readme_content = f.read()

        # If it's STILL empty, the AI generation actually failed
        if not readme_content:
            st.error("❌ ERR_AI_FAILURE: The AI agent returned an empty response.")
            st.warning("""
            **Possible Causes:**
            1. **API Quota Exceeded:** Check your AI provider's dashboard.
            2. **Context Limit Reached:** Your repository might be too large for the model to process in one go.
            3. **Content Filter:** The AI refused to answer due to safety tripwires.
            """)
            st.stop()

        # --- AUTO-SAVE LOGIC ---
        try:
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(readme_content)
            st.info(f"💾 SYSTEM LOG: **README.md** has been successfully saved to: `{readme_path}`")
        except Exception as e:
            st.warning(f"⚠️ SYSTEM ALERT: Could not auto-save. Please use the download buttons below. (Error: {e})")

        # Extract Security Audit Payload
        audit_path = os.path.join(target_dir_abs, "SECURITY_AUDIT.md")
        audit_content = ""
        if os.path.exists(audit_path):
            with open(audit_path, "r", encoding="utf-8") as f:
                audit_content = f.read()
            st.info(f"🛡️ SYSTEM LOG: **SECURITY_AUDIT.md** located at: `{audit_path}`")

        # --- RENDER COMPILED DATASET ---
        st.markdown("<div class='dataset-title'>// COMPILED_DATASET</div>", unsafe_allow_html=True)
        
        tab_readme, tab_audit, tab_raw = st.tabs(["[README_VIEW]", "[SECURITY_AUDIT]", "[RAW_MARKDOWN]"])
        
        with tab_readme:
            st.markdown(readme_content)
                
        with tab_audit:
            if audit_content:
                st.markdown(audit_content)
            else:
                st.warning("WARN: NO_SECURITY_VULNERABILITIES_LOGGED OR FILE MISSING")
                
        with tab_raw:
            st.code(readme_content, language="markdown")

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Action Buttons Row
        st.markdown("<p style='color: #00ffea;'>Manual File Controls:</p>", unsafe_allow_html=True)
        d_col1, d_col2 = st.columns(2)
        with d_col1:
            st.download_button(
                label="DOWNLOAD // BACKUP.MD", 
                data=readme_content, 
                file_name="GENERATED_README.md", 
                mime="text/markdown",
                use_container_width=True
            )
        with d_col2:
            st.download_button(
                label="FORCE OVERWRITE DOWNLOAD // README.MD", 
                data=readme_content, 
                file_name="README.md", 
                mime="text/markdown",
                use_container_width=True
            )

    except Exception as e:
        st.error(f"💥 SYSTEM_CRASH_DETECTED: {e}")
    finally:
        # Restore stdout to prevent memory leaks or system issues
        sys.stdout = old_stdout
        log_expander.expanded = False # Auto collapse when finished