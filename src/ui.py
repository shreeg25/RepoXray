import streamlit as st
import os
import sys
import time
import json
import urllib.request
import urllib.error
import re
from streamlit.runtime.scriptrunner import get_script_run_ctx
from dotenv import load_dotenv, find_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

# 1. Force find and load .env
load_dotenv(find_dotenv(), override=True)

# Logging Setup
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

# --- STREAMLIT REDIRECT FIX ---
class StreamlitRedirect:
    def __init__(self, st_empty_block):
        self.st_empty_block = st_empty_block
        self.buffer = []

    def write(self, msg):
        if msg.strip():
            self.buffer.append(msg.strip())
            if get_script_run_ctx() is not None:
                display_text = "\n".join(self.buffer[-12:])
                self.st_empty_block.code(display_text, language="bash")

    def flush(self):
        pass

# --- AI MARKDOWN SANITIZER ---
def sanitize_ai_markdown(text):
    if not text: return ""
    # Strip dangerous HTML tags that break rendering
    text = re.sub(r'<(?!https?://|!--)(?!/?[a-z0-9]+(?:\s+[a-z0-9-]+(?:=(?:"[^"]*"|\'[^\']*\'))?)*\s*/?>)[^>]+>', '', text)
    return text.strip()

# --- CODEBASE INGESTION ---
def read_codebase(target_dir, max_files=25):
    print(f">> INITIALIZING SCAN: {target_dir}")
    content = ""
    count = 0
    # Common exclusions to keep context clean
    exclude_dirs = {'.git', 'node_modules', '__pycache__', 'venv', 'env', 'dist', 'build', '.streamlit'}
    
    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if count >= max_files: break
            if file.endswith(('.py', '.js', '.ts', '.html', '.css', '.json', '.md', '.tsx', '.jsx', '.yaml', '.yml')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        print(f">> INGESTING: {file}")
                        # Grab a significant chunk of each file
                        file_body = f.read()[:4000]
                        content += f"\n--- FILE: {os.path.relpath(filepath, target_dir)} ---\n{file_body}\n"
                        count += 1
                except Exception as e:
                    print(f">> SKIP: {file} (Unreadable)")
    
    return content if content else "// [EMPTY_CODEBASE_OR_NO_MATCHING_FILES]"

# --- API HANDLER ---
@retry(
    stop=stop_after_attempt(4), 
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
def fetch_from_gemini(api_key, system_prompt, user_content):
    # Changed to gemini-2.5-flash as requested
    model_name = "gemini-2.5-flash" 
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    payload = {
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"parts": [{"text": user_content}]}],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 8192
        }
    }
    
    req = urllib.request.Request(
        url, 
        data=json.dumps(payload).encode('utf-8'), 
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        if e.code == 404:
            raise Exception(f"API 404: The model '{model_name}' was not found. Please verify your API key has access to this model.")
        elif e.code == 400:
            raise Exception(f"API 400: Bad Request. Likely context window exceeded. Details: {error_body}")
        else:
            raise Exception(f"API {e.code}: {error_body}")

# --- UI CONFIG ---
st.set_page_config(page_title="RepoXray | Terminal", page_icon="💻", layout="wide")

st.markdown("""
<style>
.stApp { background-color: #050505; color: #ffffff; font-family: 'Courier New', Courier, monospace; }
[data-testid="stSidebar"] { background-color: #08080a !important; border-right: 2px solid #ff00ff; }
.main-title { color: #00ffea !important; font-weight: 900; letter-spacing: 2px; text-shadow: 0 0 8px rgba(0,255,234,0.6); }
.magenta-line { height: 2px; background: #ff00ff; width: 100%; margin-bottom: 20px; box-shadow: 0 0 10px #ff00ff; }
.stButton>button { background: transparent !important; color: #00ffea !important; border: 1px solid #00ffea !important; border-radius: 0px !important; width: 100%; height: 3em; font-weight: bold; }
.stButton>button:hover { background: #00ffea !important; color: #000 !important; box-shadow: 0 0 15px #00ffea; }
.stMarkdown p, .stMarkdown li { font-family: 'Inter', sans-serif !important; font-size: 1.05rem; color: #cfd8dc; }
code { color: #00ffea !important; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### TERMINAL_CONFIG")
    target_dir = st.text_input("TARGET_DIRECTORY", value=".")
    
    env_key = os.environ.get("GOOGLE_API_KEY")
    api_key_input = st.text_input("AUTH_TOKEN", type="password", placeholder="Using .env if blank")
    
    st.markdown("---")
    st.markdown("### SYSTEM_STATS")
    st.caption("MODEL: gemini-2.5-flash")
    st.caption("ENGINE: 2-STAGE_NEURAL_SCAN")

# --- MAIN INTERFACE ---
st.markdown("<h1 class='main-title'>REPO_XRAY // NEURAL_SCAN</h1>", unsafe_allow_html=True)
st.markdown("<div class='magenta-line'></div>", unsafe_allow_html=True)

if st.button("INITIATE DUAL-STAGE ANALYSIS"):
    active_key = api_key_input.strip() if api_key_input.strip() else env_key
    
    if not active_key or active_key.startswith("your_"):
        st.error("ERROR: INVALID_AUTH_TOKEN. Please provide a valid Google AI API Key.")
        st.stop()

    clean_path = os.path.abspath(target_dir.strip(' "\''))
    st.session_state.target_dir_abs = clean_path
    
    if not os.path.exists(clean_path):
        st.error(f"FATAL: PATH_NOT_FOUND -> {clean_path}")
        st.stop()

    log_box = st.expander(">> LOG_STREAM", expanded=True).empty()
    old_stdout = sys.stdout
    sys.stdout = StreamlitRedirect(log_box)

    try:
        # 1. READ CODEBASE
        code_context = read_codebase(clean_path)
        
        # 2. STAGE 1: README
        print(">> STAGE_1: GENERATING TECHNICAL_README...")
        readme_prompt = """You are an expert technical documentarian. 
Create a professional README.md for this project. 
Include sections: Overview, Feature Set, Architecture Diagram (using Mermaid.js), Project Structure, Technical Stack, and Setup.

STRICT MERMAID RULES:
- MUST include a ```mermaid code block showing the system architecture.
- EVERY SINGLE NODE MAPPING MUST BE ON A NEW LINE.
- Use simple syntax: `A[Node Name] --> B[Node Name]`.
- NEVER use dashed lines (--- or --) for comments or separators INSIDE the Mermaid block.

Use Markdown only. Do not use HTML tags. Be concise but descriptive."""
        
        with st.spinner("Stage 1: Mapping Architecture..."):
            st.session_state.readme_content = sanitize_ai_markdown(fetch_from_gemini(active_key, readme_prompt, f"Codebase Context:\n{code_context}"))
        
        # 3. STAGE 2: SECURITY AUDIT
        print(">> STAGE_2: GENERATING SECURITY_REPORT...")
        audit_prompt = """You are a Cybersecurity Specialist. 
Perform an automated security audit on this code.
Look for: Hardcoded secrets, injection risks, insecure dependencies, and logical vulnerabilities.
Format by severity: [CRITICAL], [HIGH], [MEDIUM], [LOW].
For each finding, provide: Vulnerability Name, Description, and Mitigation."""
        
        with st.spinner("Stage 2: Scanning Vulnerabilities..."):
            st.session_state.audit_content = sanitize_ai_markdown(fetch_from_gemini(active_key, audit_prompt, f"Codebase Context:\n{code_context}"))

        st.session_state.scan_complete = True
        print(">> PROTOCOL_SUCCESS: OUTPUTS_STAGED.")

    except Exception as e:
        st.error(f"SYSTEM_FAILURE: {str(e)}")
    finally:
        sys.stdout = old_stdout

# --- RESULTS DISPLAY ---
if st.session_state.scan_complete:
    st.success("SCAN_COMPLETE: Neural outputs ready for review.")
    
    c1, c2, c3 = st.columns(3)
    c1.download_button("💾 DOWNLOAD README", st.session_state.readme_content, "README.md", "text/markdown", use_container_width=True)
    c2.download_button("🛡️ DOWNLOAD AUDIT", st.session_state.audit_content, "SECURITY_AUDIT.md", "text/markdown", use_container_width=True)
    
    if c3.button("📝 OVERWRITE LOCAL FILES", use_container_width=True):
        try:
            with open(os.path.join(st.session_state.target_dir_abs, "README.md"), "w", encoding="utf-8") as f: f.write(st.session_state.readme_content)
            with open(os.path.join(st.session_state.target_dir_abs, "SECURITY_AUDIT.md"), "w", encoding="utf-8") as f: f.write(st.session_state.audit_content)
            st.toast("Files updated in target directory!")
        except Exception as e: st.error(f"Write Access Denied: {e}")

    t1, t2 = st.tabs(["📄 README.md", "🔍 SECURITY_AUDIT.md"])
    with t1: st.markdown(st.session_state.readme_content)
    with t2: st.markdown(st.session_state.audit_content)