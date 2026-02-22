# 📝 AI-Powered README Generator

A sophisticated tool leveraging Large Language Models (LLMs) to automatically generate comprehensive `README.md` files for software projects. It intelligently analyzes project structure, file contents, and even performs a preliminary code health and security audit to produce a high-quality, professional README document.

## 📊 Architecture Diagram

```mermaid
graph TD
    A["`src/__main__.py` (CLI Entrypoint)"] --> C["`src/config.py` (Configuration)"]
    A --> D["`src/agents.py` (ReadmeAgent)"]
    B["`src/ui.py` (Streamlit Web UI)"] --> C
    B --> D
    D --> E["`src/tools.py` (ProjectReader)"]
    D --> F["Google GenAI API"]
    E --> G["Project Files"]
    D --> H["README.md Output"]
    A --> H
    B --> H
```

## Folder Structure

```
📁 src/
    📄 agents.py
    📄 config.py
    📄 tools.py
    📄 ui.py
    📄 __init__.py
    📄 __main__.py
```

## Architecture/Tech Stack

This project is built primarily with **Python** and leverages the following key technologies and architectural patterns:

*   **Google GenAI API**: For Large Language Model (LLM) interactions, powering the summarization, auditing, and generation capabilities.
*   **Streamlit**: Provides an intuitive and interactive web user interface for easy README generation.
*   **`python-dotenv`**: Securely loads environment variables, ensuring sensitive information like API keys are not hardcoded.
*   **`concurrent.futures.ThreadPoolExecutor`**: Utilized for parallel processing of files, enhancing performance during the "map" phase of README generation.
*   **`fnmatch`**: Used for basic `.gitignore` pattern matching to filter irrelevant files, though with acknowledged limitations.
*   **Map-Reduce Pattern**: The core logic for README generation follows a map-reduce paradigm, where individual files are summarized ("map") and then aggregated to form the final README ("reduce").
*   **Centralized Configuration**: `config.py` provides a single source of truth for application settings.

## Setup & Usage

To set up and run the README generator, follow these steps:

1.  **Clone the repository (if applicable):**
    ```bash
    git clone [your-repo-url]
    cd [your-repo-directory]
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate # On Windows use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```
    *(Note: A `requirements.txt` file needs to be created, listing dependencies like `google-generativeai`, `python-dotenv`, `streamlit`.)*

3.  **Configure your Google API Key:**
    Create a `.env` file in the project's root directory and add your Google API Key:
    ```
    GOOGLE_API_KEY=YOUR_API_KEY_HERE
    ```

4.  **Usage (Command Line Interface):**
    To generate a README for a specific directory (defaults to current directory):

    ```bash
    python -m src --path /path/to/your/project
    # or for the current directory:
    python -m src
    ```
    The generated `README.md` will be saved in the target project directory.

5.  **Usage (Streamlit Web UI):**
    To launch the interactive web application:

    ```bash
    streamlit run src/ui.py
    ```
    This will open the Streamlit application in your web browser, where you can specify the target directory and API key (optional, if already in `.env`) to generate and download your README.

## File Overview

*   ### `config.py`
    Provides a centralized configuration mechanism, loading essential settings like `GOOGLE_API_KEY` and model names from environment variables. It ensures that critical configurations are securely loaded and validated before application startup.

*   ### `agents.py`
    Defines the `ReadmeAgent` class, the core orchestrator for README generation. It implements a map-reduce process: concurrently summarizing project files (map), and then aggregating these summaries with the project structure to generate the final `README.md` (reduce). It uses Google's GenAI API with built-in retry logic and basic rate-limiting.

*   ### `tools.py`
    Contains the `ProjectReader` class, which aids LLMs by analyzing a project directory. It reads file contents, generates a textual folder structure, and filters out irrelevant content (binaries, build artifacts, `.gitignore` entries) to optimize token usage for the LLM.

*   ### `__main__.py`
    Serves as the command-line interface (CLI) entry point for the application. It parses command-line arguments, validates the target directory, and orchestrates the `ReadmeAgent` to generate a README file from the terminal.

*   ### `ui.py`
    Implements a Streamlit web application that provides a user-friendly interface for generating READMEs. It allows users to specify a target directory and API key, then leverages the `ReadmeAgent` to process the request, display the generated README, and offer it for download.

## 🕵️‍♂️ Code Health & Security Audit

This section summarizes the findings from the code audit, highlighting areas for improvement in terms of security, reliability, and maintainability.

### Security Flaws

*   **`ui.py` - `unsafe_allow_html=True`**: While currently used with controlled, hardcoded HTML for UI styling, the extensive use of `unsafe_allow_html=True` in Streamlit presents a potential Cross-Site Scripting (XSS) vulnerability if any part of the HTML were to incorporate unsanitized user input in the future.
*   **`ui.py` - API Key Handling**: The `api_key_override` is taken directly from user input (via a password field) and temporarily stored in `os.environ`. While common for Streamlit and not persistently stored, in highly sensitive or multi-user environments, this might expose the key to other processes or logs if not managed with extreme caution.

**Overall Security Posture:** The project generally adopts good practices for API key management (via `.env`), and core logic operates locally. The identified security concerns are primarily within the Streamlit UI's potential for future misuse or specific deployment scenarios.

### Bugs

*   **`tools.py` - Simplified `.gitignore` Matching**: The current implementation of `.gitignore` processing uses `fnmatch.fnmatch`, which is a significant oversimplification of the actual `.gitignore` specification. This can lead to incorrect filtering of files, either including files that should be ignored or excluding those that should be processed, thereby providing inaccurate project context to the LLM.
*   **`ui.py` - Agent Constructor Inconsistency**: The `ui.py` file attempts to instantiate `ReadmeAgent` with two different constructor signatures. This suggests a potential API inconsistency in `ReadmeAgent` itself, which could lead to runtime errors if the arguments provided do not match the expected signature in various scenarios.
*   **`ui.py` - Config Dynamic Injection**: The "DYNAMIC MEMORY INJECTION" for `Config` is a brittle workaround, relying on directly modifying `sys.modules`. This pattern indicates that the `Config` module lacks a robust mechanism for runtime updates, making the system less stable and harder to debug.

### Code Smells

*   **Missing Docstrings**:
    *   `config.py`: Lacks a module-level docstring and a docstring for the `validate` class method.
    *   `agents.py`: The `ReadmeAgent` class itself is missing a class-level docstring.
    *   `tools.py`: Several methods lack detailed docstrings (`_load_gitignore`, `_is_ignored`, `generate_folder_tree`, `read_all_valid_files`).
    *   `__main__.py`: The `main` function is missing a comprehensive docstring.
    *   `ui.py`: Lacks a module-level docstring, and some setup logic could benefit from being encapsulated in functions with docstrings.
*   **`agents.py` - Magic Numbers**: The use of several hardcoded "magic numbers" (e.g., `15000` for truncation, `3` for `max_workers`, `3` for `time.sleep`) without defining them as constants reduces readability and maintainability.
*   **`agents.py` - Manual Rate Limiting**: The `time.sleep(3)` for rate limiting is a blunt, manual approach. For a more robust and efficient solution, a token bucket algorithm or a dedicated `ratelimit` library would be preferable.
*   **`agents.py` - Embedded LLM Prompts**: LLM prompts are embedded directly as long f-strings, which can make the code blocks quite large and reduce readability.
*   **`tools.py` - Hardcoded Configuration**: `ignore_dirs` and `ignore_extensions` are hardcoded within the `ProjectReader` class. Making these configurable would improve flexibility.
*   **`tools.py`, `__main__.py` - Direct Print Statements**: The use of `print()` for warnings, status messages, and errors is less flexible than using Python's `logging` module, which allows for configurable output handling.
*   **`ui.py` - `sys.path` Manipulation**: Runtime modification of `sys.path` can lead to unpredictable module resolution. A well-defined project structure or reliance on `PYTHONPATH` is generally preferred.
*   **`ui.py` - Dynamic `.streamlit/config.toml` Generation**: Writing to a configuration file at runtime and triggering `st.rerun()` can be less transparent and potentially problematic in certain deployment scenarios compared to static configuration.
*   **`ui.py` - Flexible `ReadmeAgent` Import Logic**: The robust but flexible import attempts for `ReadmeAgent` (`agent`, `agents`, `src.agent`, etc.) indicate a lack of a canonical, fixed location for the module, which can reduce clarity.
*   **`ui.py` - Global State Mutation**: Modifying `os.environ` and directly injecting values into loaded modules (`sys.modules`) is a form of global state mutation that can complicate debugging and management in larger applications.

### Overall Assessment

The project demonstrates a solid foundation with clear architectural choices and robust error handling in key areas. The use of LLMs for advanced documentation generation is innovative and well-implemented with multithreading for performance.

However, there are several areas for improvement:

*   **Documentation:** A significant number of missing docstrings across modules and methods reduces code clarity and maintainability.
*   **Configuration Management:** The current configuration practices exhibit some brittleness, particularly in the UI, and could benefit from more robust, runtime-updatable patterns.
*   **Robustness of `tools.py`**: The `.gitignore` implementation is a critical area that needs to be brought up to spec to ensure accurate project context for the LLMs.
*   **Refinement of Utility Code**: Practices like hardcoded values, manual rate limiting, and direct print statements could be upgraded to more professional and scalable solutions (e.g., constants, dedicated rate-limiting libraries, logging).

Addressing these points would significantly enhance the project's long-term maintainability, reliability, and security posture.