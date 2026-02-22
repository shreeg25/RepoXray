# RepoXray: AI-Powered Codebase Documentation and Security Audit

RepoXray is an intelligent tool designed to automatically generate comprehensive `README.md` documentation and `SECURITY_AUDIT.md` reports for any given codebase. Leveraging Google's Gemini AI models, it scans project files, summarizes their functionality, identifies potential security concerns, and consolidates this information into well-structured Markdown reports.

## Overview

RepoXray streamlines the documentation and security review process for developers. By integrating with the Google Gemini API, it performs a deep analysis of source code, filtering out irrelevant files and focusing on the core logic. The tool employs a "Map-Reduce" strategy, where individual files are summarized and audited in parallel (Map phase), and then these insights are aggregated to produce a holistic project overview and security assessment (Reduce phase). It offers both a command-line interface (CLI) for quick scans and a Streamlit-based web UI for interactive use.

## Feature Set

*   **AI-Driven Documentation**: Automatically generates a detailed `README.md` file summarizing the project's purpose, structure, and key components.
*   **AI-Powered Security Audits**: Produces a `SECURITY_AUDIT.md` report highlighting potential vulnerabilities, bugs, and security considerations within the codebase.
*   **Intelligent File Filtering**: Skips irrelevant files and directories (e.g., `.git`, `node_modules`, `venv`, binary files) and respects `.gitignore` rules to optimize LLM context usage.
*   **Multi-threaded File Processing**: Efficiently reads and processes multiple files concurrently, speeding up the initial codebase ingestion.
*   **Robust API Interaction**: Implements retry mechanisms (`tenacity`) for Google Gemini API calls, ensuring resilience against transient network issues or rate limits.
*   **Configurable LLM Models**: Allows specification of different Gemini models for the Map and Reduce phases via environment variables.
*   **Flexible Interface**: Supports both a command-line interface (CLI) for scripting and a user-friendly Streamlit web application.
*   **Secure Credential Handling**: Manages the Google API key securely via environment variables.

## Architecture Diagram

```mermaid
graph LR
    User[User] --> Entrypoint{CLI or Streamlit UI};

    Entrypoint --> Config[Configuration (src/config.py)];
    Config --> Env[.env (API Key)];

    Entrypoint --> Agent[ReadmeAgent (src/agents.py)];

    Agent --> Reader[ProjectReader (src/tools.py)];
    Reader --> Codebase[Target Codebase];
    Codebase --> Reader;

    Reader --> Agent;

    Agent --> GeminiMap[Google Gemini API (Map Model)];
    GeminiMap --> Agent;

    Agent --> GeminiReduce[Google Gemini API (Reduce Model)];
    GeminiReduce --> Agent;

    Agent --> OutputReadme[Generated README.md];
    Agent --> OutputAudit[Generated SECURITY_AUDIT.md];
```

## Project Structure

```
.
├── .env.example             # Example file for environment variables
├── docker.compose.yaml      # Docker Compose configuration (if applicable)
├── README.md                # This documentation file
├── SECURITY_AUDIT.md        # Self-assessment security audit report
└── src/                     # Source code directory
    ├── __init__.py          # Python package initializer
    ├── __main__.py          # CLI entry point for the application
    ├── agents.py            # Core logic for AI agents (ReadmeAgent)
    ├── config.py            # Centralized configuration management
    ├── file_reader.py       # (Alternative/older) File reading utility
    ├── tools.py             # Primary file reading, filtering, and folder tree generation
    └── ui.py                # Streamlit web application interface
```

## Technical Stack

*   **Language**: Python 3.x
*   **AI/LLM**: Google Gemini API
*   **LLM Client**: `google-generativeai`
*   **Robustness**: `tenacity` (for API call retries)
*   **Configuration**: `python-dotenv` (for environment variable management)
*   **Web UI**: `streamlit`
*   **Concurrency**: `concurrent.futures` (for multi-threading)

## Setup

Follow these steps to get RepoXray up and running on your local machine.

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/RepoXray.git
cd RepoXray
```

### 2. Create and Activate a Virtual Environment

It's recommended to use a virtual environment to manage dependencies.

```bash
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

Install all required Python packages:

```bash
pip install -r requirements.txt
# (Note: A requirements.txt is assumed. If not present, you'd install individually:
# pip install google-generativeai python-dotenv tenacity streamlit)
```

### 4. Configure Google API Key

Obtain a Google Gemini API key from the [Google AI Studio](https://aistudio.google.com/app/apikey).

Create a `.env` file in the root directory of the project (next to `README.md`) and add your API key:

```dotenv
GOOGLE_API_KEY="YOUR_GEMINI_API_KEY_HERE"
MAP_MODEL="gemini-2.5-flash" # Optional: Override default map model
REDUCE_MODEL="gemini-2.5-flash" # Optional: Override default reduce model
```

**Security Note**: Ensure your `.env` file is included in your `.gitignore` to prevent accidental exposure of your API key.

### 5. Run RepoXray

You can run RepoXray using either the Command-Line Interface (CLI) or the Streamlit Web UI.

#### A. Command-Line Interface (CLI)

To generate documentation and audit reports for a target directory:

```bash
python -m src [target_directory_path]
```

*   Replace `[target_directory_path]` with the path to the codebase you want to analyze.
*   If `[target_directory_path]` is omitted, it defaults to the current directory (`.`).

**Example**:
```bash
python -m src ../my_project
```

#### B. Streamlit Web UI

To launch the interactive web application:

```bash
streamlit run src/ui.py
```

This will open a new tab in your web browser with the RepoXray UI, where you can input the target directory and initiate the analysis.