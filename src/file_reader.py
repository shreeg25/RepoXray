import os
import concurrent.futures

class ProjectReader:
    def __init__(self, target_dir):
        self.target_dir = target_dir
        # Standard directories and files to ignore during the scan
        self.ignore_dirs = {'.git', '__pycache__', 'node_modules', 'venv', '.env', '.streamlit'}
        self.ignore_exts = {
            '.pyc', '.pyo', '.png', '.jpg', '.jpeg', '.gif', '.ico', 
            '.pdf', '.zip', '.tar', '.gz', '.mp4', '.mp3', '.toml'
        }

    def generate_folder_tree(self):
        """Generates a text-based folder tree representation."""
        tree_str = []
        for root, dirs, files in os.walk(self.target_dir):
            # Modify dirs in-place to skip ignored directories
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
            
            level = root.replace(self.target_dir, '').count(os.sep)
            indent = ' ' * 4 * level
            tree_str.append(f'{indent}{os.path.basename(root)}/')
            
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                if not any(f.endswith(ext) for ext in self.ignore_exts):
                    tree_str.append(f'{subindent}{f}')
                    
        return '\n'.join(tree_str)

    def _read_single_file(self, filepath):
        """
        WORKER THREAD FUNCTION: Safely reads a single file.
        IMPORTANT: Do NOT use st.write() or st.error() here! Only print().
        """
        rel_path = os.path.relpath(filepath, self.target_dir)
        try:
            print(f"⏳ Started analyzing {rel_path}...")
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return rel_path, content
        except Exception as e:
            # Print will safely output to your custom terminal UI
            print(f"-> ❌ Error processing {rel_path}: {e}")
            return rel_path, None

    def read_all_valid_files(self):
        """Orchestrates multi-threaded file reading safely."""
        files_to_read = []
        
        # 1. Gather all valid file paths
        for root, dirs, files in os.walk(self.target_dir):
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
            for file in files:
                if not any(file.endswith(ext) for ext in self.ignore_exts):
                    files_to_read.append(os.path.join(root, file))

        results = {}
        
        print("INITIATING [MAP] PHASE: MULTI-THREADED SCANNING...")
        
        # 2. Process files in parallel safely
        # Using max_workers limits the thread count to avoid overwhelming the OS
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            # Map the worker function to our list of files
            futures = [executor.submit(self._read_single_file, fp) for fp in files_to_read]
            
            # Gather results as they complete
            for future in concurrent.futures.as_completed(futures):
                rel_path, content = future.result()
                if content is not None:
                    results[rel_path] = content

        return results