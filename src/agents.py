import os
import time
import traceback
import concurrent.futures
import google.generativeai as genai
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type, RetryError

# Robust imports to handle whether you run via `python -m src` or `streamlit run`
try:
    from src.tools import ProjectReader
    from src.config import Config
except ImportError:
    try:
        from app.tools import ProjectReader
        from app.config import Config
    except ImportError:
        from tools import ProjectReader
        from config import Config

class ReadmeAgent:
    def __init__(self, target_dir: str):
        Config.validate()
        
        # Ensure we hit Google servers securely
        genai.configure(api_key=Config.GOOGLE_API_KEY)
        self.reader = ProjectReader(target_dir)
        
        self.map_model = genai.GenerativeModel(Config.MAP_MODEL)
        self.reduce_model = genai.GenerativeModel(
            Config.REDUCE_MODEL,
            system_instruction="You are an expert technical documentation generator and security auditor. Output ONLY valid Markdown."
        )

    @retry(
        wait=wait_exponential(multiplier=3, min=10, max=60),
        stop=stop_after_attempt(5),
        retry=retry_if_exception_type(Exception)
    )
    def _call_gemini_with_retry(self, model, prompt):
        return model.generate_content(prompt)

    def _summarize_file(self, file_path: str, content: str) -> str:
        """MAP STEP: Summarizes files safely."""
        try:
            # Failsafe: Ensure content is strictly a string to prevent slice TypeErrors
            if not isinstance(content, str):
                content = str(content)
                
            truncated_content = content[:15000] 
            
            prompt = f"""
            You are an expert developer and security auditor analyzing a project.
            Review the following file: `{file_path}`.
            
            Task 1 (Summary): Provide a concise, 2-3 sentence summary of what this file does.
            Task 2 (Audit): Identify any obvious bugs, security flaws, or state "Audit: Clean".
            
            File Content:
            ```
            {truncated_content}
            ```
            """
            
            response = self._call_gemini_with_retry(self.map_model, prompt)
            
            # Failsafe: Handle cases where Gemini blocks the response due to safety settings
            if not response.parts:
                return f"Audit: Skipped. Gemini safety filters blocked the analysis of this file."
                
            return response.text.strip()
            
        except RetryError:
            return f"Audit: Failed due to repeated API timeouts/rate limits."
        except Exception as e:
            # Fallback to class name if the error message is blank
            err_msg = str(e) or type(e).__name__
            return f"Audit: Error analyzing file -> {err_msg}"

    def _process_single_file(self, file_path: str, content: str) -> str:
        """Thread wrapper: indestructible execution for a single file."""
        try:
            print(f"   ⏳ Started analyzing {file_path}...")
            
            # Skip instantly if the file reader returned empty/None data
            if not content or not str(content).strip():
                print(f"   ⏩ Skipped {file_path} (Empty or Unreadable)")
                return f"### File: `{file_path}`\nAudit: Skipped (File is empty or binary)\n"

            # Gentle pacing to respect Gemini Free Tier 15 RPM limits
            time.sleep(3)
            
            summary = self._summarize_file(file_path, content)
            print(f"   ✅ Finished analyzing {file_path}")
            return f"### File: `{file_path}`\n{summary}\n"
            
        except Exception as e:
            # This catches the "silent crashes" and exposes the real error
            err_msg = str(e) or type(e).__name__
            print(f"   -> ❌ Fatal thread error on {file_path}: {err_msg}")
            return f"### File: `{file_path}`\nAudit: Thread crashed -> {err_msg}\n"

    def generate(self) -> str:
        print(f"🔍 Scanning project directory: {self.reader.root_dir}")
        folder_tree = self.reader.generate_folder_tree()
        valid_files = self.reader.read_all_valid_files()
        
        print(f"📄 Found {len(valid_files)} files. Starting Map-Reduce concurrent summarization...")
        
        file_summaries = []
        
        # Lowered max workers to 2 to prevent instantly slamming the Free Tier limits
        max_workers = min(2, len(valid_files)) if valid_files else 1
        
        # --- STREAMLIT THREADING FIX ---
        # Capture Streamlit context if running in UI mode
        try:
            from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx
            ctx = get_script_run_ctx()
        except ImportError:
            ctx = None

        def _process_with_context(path, content):
            # Inject the context into the background thread before it runs
            if ctx:
                add_script_run_ctx(ctx=ctx)
            return self._process_single_file(path, content)
        # ---------------------------------

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {
                executor.submit(_process_with_context, path, content): path 
                for path, content in valid_files.items()
            }
            
            for future in concurrent.futures.as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    # We grab the result. If a catastrophic error somehow escaped our try/catch, we log it.
                    result = future.result()
                    file_summaries.append(result)
                except Exception as exc:
                    err_msg = str(exc) or type(exc).__name__
                    print(f"   -> ❌ Thread pool rejected {file_path}: {err_msg}")
                    file_summaries.append(f"### File: `{file_path}`\nAudit: Rejected by thread pool -> {err_msg}\n")
            
        combined_summaries = "\n".join(file_summaries)

        print("🧠 Compiling final README.md with Architecture Diagram and Health Audit...")
        
        final_prompt = f"""
        You are an elite AI technical documentation generator. Write a comprehensive `README.md` 
        for a software project based on the folder structure and file summaries.
        
        CRITICAL FORMATTING RULES:
        - Use double newlines between paragraphs and sections.
        - ALWAYS properly close your code blocks with triple backticks (```).
        
        Sections:
        1. **Title & Description**: Catchy title and purpose.
        2. **📊 Architecture Diagram**: Generate a `mermaid` block flowchart (`graph TD`). Wrap node labels in double quotes!
        3. **Folder Structure**: Included below.
        4. **Setup & Usage**: Step-by-step instructions.
        5. **File Overview & Security Audit**: Summarize the files and report the aggregated health audits.

        --- Folder Tree ---
        {folder_tree}
        
        --- File Summaries & Audits ---
        {combined_summaries}
        
        Output ONLY valid Markdown.
        """

        try:
            print("⏳ Sending final request to LLM (this might take a moment)...")
            response = self._call_gemini_with_retry(self.reduce_model, final_prompt)
            final_markdown = response.text.strip()
            
            output_path = os.path.join(self.reader.root_dir, "GENERATED_README.md")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(final_markdown)
                
            print(f"✅ Success! README saved to {output_path}")
            return final_markdown
            
        except Exception as e:
            err_msg = str(e) or type(e).__name__
            print(f"❌ Error generating final README: {err_msg}")
            return ""