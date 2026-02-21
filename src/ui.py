import streamlit as st
import os
import time

# --- AUTO-DARK THEME ENFORCER ---
def enforce_dark_theme():
    """Creates a .streamlit/config.toml file dynamically to force dark mode."""
    os.makedirs(".streamlit", exist_ok=True)
    config_path = ".streamlit/config.toml"
    
    theme_config = """
[theme]
base="dark"
primaryColor="#ff00ff"
backgroundColor="#050508"
secondaryBackgroundColor="#0a0a10"
textColor="#e0e0e0"
font="monospace"
"""
    needs_update = False
    if not os.path.exists(config_path):
        needs_update = True
    else:
        with open(config_path, "r") as f:
            if 'base="dark"' not in f.read():
                needs_update = True
                
    if needs_update:
        with open(config_path, "w") as f:
            f.write(theme_config)
        return True
    return False

# Attempt to import your ReadmeAgent. 
try:
    from src.agents import ReadmeAgent
except ImportError:
    try:
        from agents import ReadmeAgent
    except ImportError:
        st.error("SYSTEM FAILURE: Could not import ReadmeAgent.")

# --- UI Configuration ---
st.set_page_config(
    page_title="SYS.OP // REPO_XRAY",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Force a reload immediately if the dark theme config was just created
if enforce_dark_theme():
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()

# --- CYBERPUNK CSS OVERRIDE ---
st.markdown("""
<style>
    /* Global Background and Text */
    .stApp {
        background-color: #050508;
        background-image: 
            linear-gradient(rgba(0, 255, 204, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 255, 204, 0.03) 1px, transparent 1px);
        background-size: 30px 30px;
        color: #e0e0e0;
        font-family: 'Courier New', Courier, monospace;
    }

    /* Headers */
    .cyber-header {
        font-family: 'Courier New', Courier, monospace;
        font-size: 3rem;
        font-weight: 900;
        color: #fff;
        text-transform: uppercase;
        letter-spacing: 4px;
        margin-bottom: 0;
        text-shadow: 0 0 5px #00ffcc, 0 0 15px #00ffcc, 0 0 30px #00ffcc;
        border-bottom: 2px solid #ff00ff;
        padding-bottom: 10px;
    }
    .cyber-subheader {
        font-family: 'Courier New', Courier, monospace;
        font-size: 1rem;
        color: #ff00ff;
        margin-top: 5px;
        margin-bottom: 2rem;
        letter-spacing: 2px;
        text-shadow: 0 0 5px rgba(255, 0, 255, 0.5);
    }

    /* Sidebar Customization */
    [data-testid="stSidebar"] {
        background-color: #0a0a10 !important;
        border-right: 1px solid #ff00ff;
        box-shadow: 5px 0 15px rgba(255, 0, 255, 0.1);
    }
    
    /* Input Fields */
    .stTextInput > div > div > input {
        background-color: #000000 !important;
        color: #00ffcc !important;
        border: 1px solid #333 !important;
        border-bottom: 2px solid #00ffcc !important;
        border-radius: 0px !important;
        font-family: monospace;
    }
    .stTextInput > div > div > input:focus {
        border-color: #ff00ff !important;
        box-shadow: 0 4px 10px rgba(255, 0, 255, 0.2) !important;
    }

    /* Primary Buttons */
    .stButton > button {
        background-color: #050508 !important;
        border: 1px solid #00ffcc !important;
        color: #00ffcc !important;
        border-radius: 0px !important;
        font-family: monospace;
        font-weight: bold;
        letter-spacing: 2px;
        text-transform: uppercase;
        width: 100%;
        box-shadow: 0 0 10px rgba(0, 255, 204, 0.2) !important;
        transition: all 0.2s ease-in-out;
    }
    .stButton > button:hover {
        background-color: #00ffcc !important;
        color: #000 !important;
        box-shadow: 0 0 20px rgba(0, 255, 204, 0.6) !important;
        border-color: #fff !important;
    }

    /* Data/Status Containers */
    [data-testid="stStatusWidget"] {
        background-color: #000 !important;
        border: 1px solid #ff00ff !important;
        border-radius: 0px !important;
        color: #fff !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #050508;
        border-bottom: 1px solid #333;
    }
    .stTabs [data-baseweb="tab"] {
        color: #666;
        border-radius: 0px;
        font-family: monospace;
        text-transform: uppercase;
    }
    .stTabs [aria-selected="true"] {
        color: #00ffcc !important;
        border-bottom: 2px solid #00ffcc !important;
        text-shadow: 0 0 8px rgba(0, 255, 204, 0.5);
    }

    /* Dividers */
    hr {
        border-color: #333 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar (Command Line Interface) ---
with st.sidebar:
    st.markdown("<h2 style='color: #00ffcc; font-family: monospace;'>TERMINAL_ACCESS</h2>", unsafe_allow_html=True)
    st.write("`AWAITING CONFIGURATION PARAMS...`")
    
    st.divider()
    
    target_directory = st.text_input(
        "TARGET_DIR [PATH]", 
        value=".", 
        help="Absolute or relative path to target node."
    )
    
    api_key_override = st.text_input(
        "AUTH_TOKEN [API_KEY]", 
        type="password", 
        help="Override default environment authentication token."
    )
    
    st.divider()
    st.markdown("`<SYS_ID: EPOCH_X_NASIKO>`", unsafe_allow_html=True)
    st.markdown("`<STATUS: ONLINE>`", unsafe_allow_html=True)

# --- Main Canvas ---
st.markdown('<p class="cyber-header">REPO_XRAY // ORCHESTRATOR</p>', unsafe_allow_html=True)
st.markdown('<p class="cyber-subheader">>> NEURAL NETWORK CODEBASE ANALYSIS ENGAGED</p>', unsafe_allow_html=True)

# Container for the generate button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    generate_btn = st.button("EXECUTE // MAP_REDUCE SEQUENCE")

# --- Execution Logic ---
if generate_btn:
    abs_path = os.path.abspath(target_directory)
    if not os.path.exists(abs_path):
        st.error(f"FATAL ERROR: PATH_NOT_FOUND -> '{abs_path}'")
        st.stop()
        
    if not os.path.isdir(abs_path):
        st.error(f"FATAL ERROR: INVALID_NODE_TYPE -> '{abs_path}' IS FILE, EXPECTED DIR")
        st.stop()

    with st.status("INITIALIZING_PROTOCOL...", expanded=True) as status:
        try:
            st.write(f"> MOUNTING DIRECTORY: `{abs_path}`")
            time.sleep(0.5)
            
            if api_key_override:
                st.write("> OVERRIDING DEFAULT AUTH_TOKEN...")
                os.environ["GOOGLE_API_KEY"] = api_key_override
                os.environ["OPENAI_API_KEY"] = api_key_override
            
            st.write("> ENGAGING LLM CORES...")
            
            try:
                agent = ReadmeAgent(target_dir=abs_path) 
            except TypeError:
                agent = ReadmeAgent(api_key=os.environ.get("OPENAI_API_KEY", ""), target_dir=abs_path)
            
            st.write("> INITIATING [MAP] PHASE: MULTI-THREADED SCANNING...")
            st.write("> INITIATING [REDUCE] PHASE: DATA SYNTHESIS...")
            
            if hasattr(agent, "generate"):
                final_markdown = agent.generate()
            else:
                final_markdown = agent.generate_readme()

            status.update(label="PROTOCOL COMPLETE // DOCUMENTATION GENERATED", state="complete", expanded=False)
            
            st.session_state['generated_readme'] = final_markdown

        except Exception as e:
            status.update(label="CRITICAL FAILURE IN SEQUENCE", state="error", expanded=True)
            st.error(f"SYS_EXCEPTION: {str(e)}")
            st.stop()

# --- Display Results ---
if 'generated_readme' in st.session_state:
    st.divider()
    st.markdown("<h3 style='color: #ff00ff; font-family: monospace; letter-spacing: 2px;'>// COMPILED_DATASET</h3>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["[RENDERED_VIEW]", "[RAW_MARKDOWN]"])
    
    with tab1:
        st.markdown(st.session_state['generated_readme'])
        
    with tab2:
        st.code(st.session_state['generated_readme'], language="markdown")
        
    st.write("") # Spacing
    st.download_button(
        label="DOWNLOAD // README.MD",
        data=st.session_state['generated_readme'],
        file_name="GENERATED_README.md",
        mime="text/markdown"
    )