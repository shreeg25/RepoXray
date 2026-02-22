import streamlit as st
import os
import sys
import time
import json
import urllib.request
import urllib.error
from streamlit.runtime.scriptrunner import get_script_run_ctx
from dotenv import load_dotenv, find_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

# 1. Force find and load .env from anywhere in the project tree
load_dotenv(find_dotenv(), override=True)

# Set up basic logging for Tenacity
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- INITIALIZE SESSION STATE ---
if "readme_content" not in st.session_state:
    st.session_state.readme_content = ""
if "audit_content" not in st.session_state:
    st.session_state.audit_content = ""
if "scan_complete" not in st.session_state:
    st.session_state.scan_complete = False
if "target_dir_abs" not in st.session_state:
    st.session_state.target_dir_abs = ""

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

# Helper function to read codebase files for the API
def read_codebase(target_dir, max_files=15):
    print(f">> SCANNING DIRECTORY: {target_dir}")
    content = ""
    count = 0
    for root, _, files in os.walk(target_dir):
        for file in files:
            if count >= max_files:
                break
            # Only read common source code extensions to avoid binaries
            if file.endswith(('.py', '.js', '.ts', '.html', '.css', '.json', '.md', '.tsx', '.jsx')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        print(f">> INGESTING FILE: {file}")
                        # Limit to first 2000 chars per file to save context limits
                        content += f"\n--- {filepath} ---\n{f.read()[:2000]}\n"
                    count += 1
                except Exception as e:
                    print(f">> ERR_READING: {file} ({e})")
        if count >= max_files:
            print(">> MAX_FILE_LIMIT_REACHED. HALTING INGESTION.")
            break
            
    if not content:
        print(">> WARN: NO VALID SOURCE FILES FOUND. PROCEEDING WITH EMPTY CONTEXT.")
        return "// No readable source code found in directory."
    return content

# --- TENACITY RETRY LOGIC FOR API CALLS ---
@retry(
    stop=stop_after_attempt(4), 
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
def fetch_from_gemini(url, payload):
    print(">> TRANSMITTING PACKETS TO NEURAL API (Awaiting Response)...")
    req = urllib.request.Request(
        url, 
        data=json.dumps(payload).encode('utf-8'), 
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))

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
.stDownloadButton>button {
    background-color: #1a0033 !important;
    color: #ff00ff !important;
    border: 1px solid #ff00ff !important;
}

/* System Logs / Success Box */
[data-testid="stAlert"] {
    background-color: #002200 !important;
    border: 1px solid #00ff41 !important;
    color: #00ff41 !important;
    border-radius: 4px;
}

/* Markdown specific fixes to ensure readability over the background */
.stMarkdown p, .stMarkdown li {
    font-family: sans-serif !important;
    font-size: 1.05rem !important;
    line-height: 1.6;
    color: #e2e8f0;
}
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    color: #00ffea !important;
    font-family: 'Courier New', Courier, monospace !important;
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

col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    start_scan = st.button("GENERATE README & SECURITY AUDIT", use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

if start_scan:
    if api_key_input.strip():
        os.environ["GOOGLE_API_KEY"] = api_key_input.strip()

    current_key = os.environ.get("GOOGLE_API_KEY", "").strip()
    dummy_keys = ["", "your_api_key_here", "insert_key_here", "<your_api_key>"]
    
    is_mock = False
    if not current_key or current_key.lower() in dummy_keys:
        st.warning("⚠️ AUTH_TOKEN MISSING OR INVALID. FALLING BACK TO MOCK MODE...")
        is_mock = True

    clean_target_dir = target_dir.strip(' "\'')
    target_dir_abs = os.path.abspath(clean_target_dir)
    st.session_state.target_dir_abs = target_dir_abs
    
    if not os.path.exists(target_dir_abs):
        st.error(f"❌ ERR_DIR_NOT_FOUND: Path does not exist -> {target_dir_abs}")
        st.stop()
        
    log_expander = st.expander(">> LIVE_TERMINAL_LOGS... (Extracting Context)", expanded=True)
    log_container = log_expander.empty()
    
    old_stdout = sys.stdout
    sys.stdout = StreamlitRedirect(log_container)
    
    try:
        with st.spinner("BREACHING_MAINFRAME & INITIATING DEEP SCAN... [EST. TIME: 1-3 MINS] ⏳"):
            
            if is_mock:
                print(">> INITIALIZING OFFLINE MOCK HEURISTICS...")
                time.sleep(2)
                st.session_state.readme_content = "# MOCK README\nTest data."
                st.session_state.audit_content = "# MOCK AUDIT\nTest data."
                st.session_state.scan_complete = True
                
            else:
                code_context = read_codebase(target_dir_abs)
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={current_key}"
                
                # UPDATED PROMPT: Strict Markdown & Mermaid rules to prevent rendering crashes
                system_prompt = """You are RepoXray, an elite software architecture and cybersecurity AI. 
Your task is to analyze the provided codebase and generate two comprehensive documents.

CRITICAL RULES TO PREVENT RENDERING CRASHES:
1. JSON ONLY: Respond ONLY with a valid JSON object containing EXACTLY two keys: "readme" and "security_audit".
2. STRICT MARKDOWN: Use ONLY standard Markdown formatting. DO NOT use raw HTML tags (like <ul>, <li>, <code>, <br>). Use *, -, or numbers for lists. Use backticks strictly for code blocks.
3. MERMAID DIAGRAM RULES: You MUST include a ```mermaid architecture diagram. 
   - CRITICAL: Node labels MUST NOT contain backticks (`), quotes ("), or brackets ([]) inside the text.
   - Good Example: A[CLI Entrypoint] --> B[Core Engine]
   - Bad Example (WILL CRASH): A[`src/main.py`] --> B(Engine)

REQUIREMENTS FOR "readme":
- Cyberpunk-themed professional header.
- 🎯 PROJECT PURPOSE: What real-world problem does it solve?
- ✨ CORE FEATURES: DEDUCE THE ACTUAL FUNCTIONALITY. Provide a highly detailed bulleted list.
- 🛠️ TECH STACK
- 🏗️ SYSTEM ARCHITECTURE: Mermaid.js diagram (Following the strict rules above).
- 🚀 SETUP INSTRUCTIONS

REQUIREMENTS FOR "security_audit":
- Executive summary of the security posture.
- Threat modeling overview.
- Detailed vulnerability analysis (CWE classifications, Severity, Description, Remediation)."""

                payload = {
                    "systemInstruction": {
                        "parts": [{"text": system_prompt}]
                    },
                    "contents": [{"parts": [{"text": f"Analyze this codebase and fully populate the JSON response.\n\n{code_context}"}]}],
                    "generationConfig": {
                        "responseMimeType": "application/json",
                        "responseSchema": {
                            "type": "OBJECT",
                            "properties": {
                                "readme": {"type": "STRING"},
                                "security_audit": {"type": "STRING"}
                            },
                            "required": ["readme", "security_audit"]
                        }
                    }
                }
                
                result = fetch_from_gemini(url, payload)
                json_string = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '{}')
                
                json_string = json_string.strip()
                if json_string.startswith('```json'):
                    json_string = json_string[7:]
                elif json_string.startswith('```'):
                    json_string = json_string[3:]
                if json_string.endswith('```'):
                    json_string = json_string[:-3]
                    
                parsed_data = json.loads(json_string.strip())
                
                st.session_state.readme_content = parsed_data.get('readme', 'No README generated.')
                st.session_state.audit_content = parsed_data.get('security_audit', parsed_data.get('securityAudit', '# Audit failed to generate.'))
                st.session_state.scan_complete = True

        sys.stdout = old_stdout
        
    except Exception as e:
        sys.stdout = old_stdout
        st.error(f"💥 SYSTEM_CRASH_DETECTED: {e}")
        st.session_state.scan_complete = False
    finally:
        sys.stdout = old_stdout
        log_expander.expanded = False


# --- RENDER RESULTS & ACTION BUTTONS ---
if st.session_state.scan_complete:
    st.success("✓ PROTOCOL COMPLETE // NEURAL SCAN FINISHED")
    
    # Restored Action Buttons!
    col_act1, col_act2, col_act3 = st.columns(3)
    
    with col_act1:
        st.download_button(
            label="⬇️ DOWNLOAD README.md",
            data=st.session_state.readme_content,
            file_name="README.md",
            mime="text/markdown",
            use_container_width=True
        )
        
    with col_act2:
        st.download_button(
            label="⬇️ DOWNLOAD SECURITY_AUDIT.md",
            data=st.session_state.audit_content,
            file_name="SECURITY_AUDIT.md",
            mime="text/markdown",
            use_container_width=True
        )
        
    with col_act3:
        if st.button("💾 OVERWRITE LOCAL FILES", use_container_width=True):
            try:
                readme_path = os.path.join(st.session_state.target_dir_abs, "README.md")
                audit_path = os.path.join(st.session_state.target_dir_abs, "SECURITY_AUDIT.md")
                with open(readme_path, "w", encoding="utf-8") as f:
                    f.write(st.session_state.readme_content)
                with open(audit_path, "w", encoding="utf-8") as f:
                    f.write(st.session_state.audit_content)
                st.success(f"Files written directly to `{st.session_state.target_dir_abs}`!")
            except Exception as e:
                st.error(f"Failed to overwrite files: {e}")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- TABS FOR VIEWING ---
    tab1, tab2 = st.tabs(["README.md", "SECURITY_AUDIT.md"])
    
    with tab1:
        # Added unsafe_allow_html=True as a fail-safe in case the AI still sneaks some HTML through
        st.markdown(st.session_state.readme_content, unsafe_allow_html=True)
        
    with tab2:
        st.markdown(st.session_state.audit_content, unsafe_allow_html=True)