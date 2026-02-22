# 🚀 RepoXray: Codebase Architect & Sentinel
### Your AI-Powered Documentation & Security Nexus
In the neon-drenched future, clarity and security are paramount. RepoXray isn't just another program; it's your digital architect and sentinel, a robust AI orchestrator designed to tame the chaos of complex codebases. Forged in the crucible of the Epoch X Nasiko Hackathon, RepoXray transcends basic LLM wrappers, transforming raw, sprawling code into pristine, insightful documentation and critical security audits. It's the silent partner that ensures your projects are not only well-understood but also fortified against the unseen threats lurking in the digital ether.

### 🎯 Project Purpose
RepoXray serves as an indispensable tool for developers, project managers, and security professionals navigating the intricate landscapes of modern software development. It automates the arduous and error-prone process of documentation and initial security assessment, providing immediate, high-quality insights into any codebase. By leveraging advanced AI, RepoXray solves the critical problem of outdated or missing documentation, allowing teams to quickly onboard new members, understand legacy systems, and proactively identify security vulnerabilities. It delivers a comprehensive overview of project purpose, architecture, and potential weak points, acting as a crucial bridge between code complexity and human comprehension.

### ✨ Core Features
- **AI-Powered Documentation Generation:** Analyzes codebase structure and content to autonomously generate a professional, detailed `README.md`, encapsulating project purpose, features, and architectural overview using Google Gemini's generative AI.
- **Integrated Security Posture Audit:** Simultaneously scans the code for potential security vulnerabilities and considerations, generating a `SECURITY_AUDIT.md` that identifies weaknesses and suggests remediations.
- **Intelligent File Filtering:** Employs sophisticated filtering mechanisms (`.gitignore` awareness, common ignore directories, binary/media file extensions) to focus AI analysis only on relevant source code, optimizing token usage and preventing sensitive data exposure.
- **Robust LLM Interaction:** Utilizes `tenacity` for exponential backoff and retries on Google Gemini API calls, ensuring resilience against transient network issues or rate limits.
- **Flexible Deployment:** Supports both a command-line interface (CLI) for batch processing and a Streamlit-based graphical user interface (GUI) for interactive use.
- **Configurable AI Models:** Allows specification of different Gemini models (`gemini-2.5-flash` by default) for mapping (summarization) and reduction (final output generation) steps, offering flexibility for performance and cost optimization.
- **Secure API Key Handling:** Integrates `python-dotenv` for secure loading of the `GOOGLE_API_KEY` from environment variables, never hardcoding sensitive credentials.

### 🏗️ System Architecture
RepoXray employs a modular, agent-based architecture, utilizing a "Map-Reduce" pattern for AI processing. It supports both a CLI and a Streamlit GUI for user interaction.

```mermaid
graph TD
    User[User Input: Target Directory]

    subgraph Entrypoints
        A[CLI Entrypoint: __main__.py]
        B[Streamlit GUI: ui.py]
    end

    User --> A
    User --> B

    A --> C[Config Validation & Setup]
    B --> C

    C --> D[ReadmeAgent Initialization]

    subgraph Core AI Processing (ReadmeAgent)
        D --> E[ProjectReader: Scan & Filter Files]
        E --> F[Multi-threaded File Reading]
        F --> G{File Content & Path}

        G -- Map Step --> H[Gemini MAP_MODEL: Summarize File Chunks]
        H --> I[File Summaries]

        I -- Reduce Step --> J[Gemini REDUCE_MODEL: Generate README & Audit]
    end

    J --> K[Output: README.md]
    J --> L[Output: SECURITY_AUDIT.md]

    K --> User
    L --> User

    subgraph Shared Utilities
        Config[Config Class]
        Tools[ProjectReader / File Utils]
        Tenacity[API Retry Logic]
    end

    C --> Config
    D --> Config
    D --> Tools
    H --> Tenacity
    J --> Tenacity

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#f9f,stroke:#333,stroke-width:2px
    style J fill:#bbf,stroke:#333,stroke-width:2px
```

### ⚙️ Setup and Installation
1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/your-repo/RepoXray.git
    cd RepoXray
    ```

2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt # (Assuming a requirements.txt exists with: google-generativeai python-dotenv tenacity streamlit)
    ```

4.  **Configure API Key:**
    Obtain a Google Gemini API key from the [Google AI Studio](https://aistudio.google.com/app/apikey).
    Create a `.env` file in the root directory of the project and add your API key:
    ```
    GOOGLE_API_KEY="YOUR_GEMINI_API_KEY"
    ```

### 🚀 Usage
#### Command-Line Interface (CLI)
For analyzing a target directory and generating `README.md` and `SECURITY_AUDIT.md` files:
```bash
python -m src.__main__ [target_directory_path]
```
-   `[target_directory_path]` is optional. If not provided, it defaults to the current working directory (`.`).

Example:
```bash
python -m src.__main__ ../my_project
```
This will generate `README.md` and `SECURITY_AUDIT.md` in the directory where you run the command.

#### Streamlit Graphical User Interface (GUI)
For an interactive experience:
```bash
streamlit run src/ui.py
```
This will open a web application in your browser where you can input the target directory and view the generated documentation and audit reports directly.

### 📜 Output
RepoXray generates two primary files:
-   `README.md`: A comprehensive project overview, including purpose, features, and architectural breakdown.
-   `SECURITY_AUDIT.md`: A detailed report on potential security vulnerabilities, considerations, and suggested mitigations.

### 🤝 Contributing
Contributions are welcome! Please refer to the project's GitHub repository for guidelines on how to contribute.

### 📄 License
This project is licensed under the [MIT License](LICENSE).