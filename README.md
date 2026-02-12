# 🤖 RepoXray: AI-Powered Project README Generator

**RepoXray** is an AI orchestrator built for the **Epoch X Nasiko Hackathon**. It automatically transforms complex, messy codebases into professional, high-quality documentation.

Unlike standard AI prompt wrappers, RepoXray is specifically engineered to handle massive, nested repository structures without hitting LLM token limits or crashing on edge cases.

## ✨ Key Features 

1. **Map-Reduce Architecture (Token Limit Savior)**
   Instead of dumping an entire codebase into one prompt, RepoXray first concurrently summarizes individual files (Map), and then synthesizes those bite-sized summaries into a master README (Reduce).

2. **Bulletproof Edge-Case Handling**
   Automatically detects and skips zero-byte files, unreadable binaries (images, compiled code), and deeply respects `.gitignore` rules to prevent scanning junk folders like `node_modules` or `.venv`.

3. **Production-Grade API Resiliency**
   Implements automatic exponential backoff. If the LLM API hits rate limits during a large folder scan, the agent pauses and retries instead of failing outright.

4. **Integrated Security & Health Audit**
   During the file-scanning phase, the agent passively audits the code for vulnerabilities, hardcoded secrets, and missing docstrings, aggregating them into a final health report.

## 🚀 Getting Started

### Prerequisites

* Python 3.10+
* A [Google Gemini API Key](https://aistudio.google.com/)

### 1. Setup & Installation

Clone the repository and install the required dependencies:

```bash
git clone [https://github.com/yourusername/repoxray.git](https://github.com/yourusername/repoxray.git)
cd repoxray
pip install -r requirements.txt
```

Create a .env file in the root directory and add your API key:
```bash
GOOGLE_API_KEY=your_gemini_api_key_here
MAP_MODEL=gemini-2.5-flash
REDUCE_MODEL=gemini-2.5-flash
```

### 2. Usage

Run the agent from your terminal.

To document the current directory:
```bash
python -m app .
```

To document a specific project path:
```bash
python -m app /path/to/your/project
```

Once completed, the agent will generate a highly structured GENERATED_README.md file directly in the target directory.

**⚖️ Hackathon Criteria Alignment**

Goal Satisfaction: Successfully generates a comprehensive, single Markdown file representing an entire complex folder structure.

Prompt & Coding Style: Highly modular codebase utilizing decoupled logic, multi-threading, and advanced map-reduce prompting.

Edge Case Handling: Failsafes built-in for unreadable files, context window limits, and API rate limiting.
