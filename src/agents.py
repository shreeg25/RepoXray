import os
import time
import concurrent.futures
from google import genai
from google.genai import types, errors
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type, RetryError
from src.tools import ProjectReader
from src.config import Config

class ReadmeAgent:
    def __init__(self, target_dir: str):
        # Validate config before starting
        Config.validate()
        
        # Initialize the new GenAI client
        self.client = genai.Client(api_key=Config.GOOGLE_API_KEY)
        self.reader = ProjectReader(target_dir)
        
        # Store model names
        self.map_model_name = Config.MAP_MODEL
        self.reduce_model_name = Config.REDUCE_MODEL
        
        # Set up system instructions for the reduce step
        self.reduce_config = types.GenerateContentConfig(
            system_instruction="You are an expert technical documentation generator and security auditor. Output ONLY valid Markdown."
        )

    @retry(
        wait=wait_exponential(multiplier=3, min=15, max=120),
        stop=stop_after_attempt(10),
        retry=retry_if_exception_type((errors.APIError, errors.ClientError))
    )
    def _call_gemini_with_retry(self, model_name, prompt, config=None):
        """Helper method to call Gemini with automatic retries on API errors (like Quota/429)."""
        return self.client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=config
        )

    def _summarize_file(self, file_path: str, content: str) -> str:
        """MAP STEP: Summarizes files AND performs a security/health audit."""
        truncated_content = content[:15000] 
        
        # USP 3: We instruct the Map step to also look for bugs and security flaws
        prompt = f"""
        You are an expert developer and security auditor analyzing a project.
        Review the following file: `{file_path}`.
        
        Task 1 (Summary): Provide a concise, 2-3 sentence summary of what this file does, its main classes/functions, and its role.
        Task 2 (Audit): Briefly identify any obvious bugs, security flaws (e.g., hardcoded passwords/keys), code smells, or completely missing docstrings. If the file is healthy, state "Audit: Clean".
        
        CRITICAL: If the code looks incomplete or broken, describe its INTENDED purpose based on naming conventions.
        
        File Content:
        ```
        {truncated_content}
        ```
        """
        try:
            response = self._call_gemini_with_retry(self.map_model_name, prompt)
            return response.text.strip()
        except RetryError as re:
            return f"Could not analyze file due to repeated API errors: {re.last_attempt.exception()}"
        except Exception as e:
            return f"Could not analyze file due to error: {str(e)}"

    def _process_single_file(self, file_path: str, content: str) -> str:
        """Helper for multithreading: analyzes a single file and formats the output."""
        print(f"   ⏳ Started analyzing {file_path}...")
        # Gentle pacing to avoid instantly slamming the Free Tier RPM limit
        time.sleep(3)
        summary = self._summarize_file(file_path, content)
        print(f"   ✅ Finished analyzing {file_path}")
        return f"### File: `{file_path}`\n{summary}\n"

    def generate(self) -> str:
        """REDUCE STEP: Orchestrates the final README and Mermaid Graph generation."""
        print(f"🔍 Scanning project directory: {self.reader.root_dir}")
        folder_tree = self.reader.generate_folder_tree()
        valid_files = self.reader.read_all_valid_files()
        
        print(f"📄 Found {len(valid_files)} valid files. Starting Map-Reduce concurrent summarization...")
        print(f"⚠️  NOTE: If it pauses, it is automatically waiting out the Gemini Free Tier limit.")
        
        file_summaries = []
        
        max_workers = min(3, len(valid_files)) if valid_files else 1
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {
                executor.submit(self._process_single_file, path, content): path 
                for path, content in valid_files.items()
            }
            
            for future in concurrent.futures.as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    file_summaries.append(result)
                except Exception as exc:
                    print(f"   -> ❌ Error processing {file_path}: {exc}")
            
        combined_summaries = "\n".join(file_summaries)

        print("🧠 Compiling final README.md with Architecture Diagram and Health Audit...")
        
        # USP 1 & USP 3: Instructing the final generation to output Mermaid and the Health Report
        final_prompt = f"""
        You are an elite AI technical documentation generator. Your task is to write a comprehensive, professional `README.md` 
        for a software project based on the provided folder structure and file summaries.
        
        CRITICAL FORMATTING RULES:
        - Use double newlines between paragraphs and sections so the Markdown renders correctly.
        - ALWAYS properly close your code blocks with triple backticks (```).
        
        Your output MUST include the following sections exactly:
        
        1. **Title & Description**: Catchy title and a clear project purpose.
        2. **📊 Architecture Diagram**: Generate a `mermaid` code block containing a flowchart (`graph TD`). 
           CRITICAL MERMAID RULE: You MUST wrap all node labels in double quotes to prevent rendering errors (e.g., `A["app/__main__.py"] --> B["app/config.py"]`). Do not put slashes or dots in the node IDs themselves, only in the quoted labels!
        3. **Folder Structure**: Include the exact folder tree provided below inside a standard code block.
        4. **Architecture/Tech Stack**: Infer the technologies used.
        5. **Setup & Usage**: Provide step-by-step instructions on how to run this. Ensure the bash script is inside a closed ```bash block.
        6. **File Overview**: Provide a brief overview of key components.
        7. **🕵️‍♂️ Code Health & Security Audit**: Aggregate the "Audit" notes from the file summaries. Create a professional summary of the repository's health.

        --- Folder Tree ---
        {folder_tree}
        
        --- File Summaries & Audits ---
        {combined_summaries}
        
        Output ONLY valid Markdown.
        """

        try:
            print("⏳ Sending final request to LLM (this might take a moment due to size)...")
            response = self._call_gemini_with_retry(self.reduce_model_name, final_prompt, config=self.reduce_config)
            final_markdown = response.text.strip()
            
            output_path = os.path.join(self.reader.root_dir, "GENERATED_README.md")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(final_markdown)
                
            print(f"✅ Success! README saved to {output_path}")
            return final_markdown
            
        except RetryError as re:
            print(f"❌ API Error: Retries exhausted. The API is consistently rejecting the request.")
            print(f"   -> Underlying Error: {re.last_attempt.exception()}")
            return ""
        except Exception as e:
            print(f"❌ Error generating final README: {e}")
            return ""