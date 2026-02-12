import os
import fnmatch

class ProjectReader:
    """
    Tool for reading project files, generating folder structures, 
    and filtering out irrelevant/binary files to save LLM context window.
    """
    
    def __init__(self, root_dir: str):
        self.root_dir = os.path.abspath(root_dir)
        
        # Directories to ignore to prevent token overflow
        self.ignore_dirs = {
            '.git', 'node_modules', 'venv', '.venv', 'env', 
            '__pycache__', 'dist', 'build', '.idea', '.vscode'
        }
        
        # Binary/media extensions to ignore
        self.ignore_extensions = {
            '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', 
            '.pdf', '.exe', '.dll', '.so', '.pyc', '.zip', 
            '.tar', '.gz', '.mp4', '.mp3', '.wav'
        }
        
        self.gitignore_patterns = self._load_gitignore()

    def _load_gitignore(self) -> list:
        gitignore_path = os.path.join(self.root_dir, '.gitignore')
        patterns = []
        if os.path.exists(gitignore_path):
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.append(line)
        return patterns

    def _is_ignored(self, path: str, is_dir: bool = False) -> bool:
        name = os.path.basename(path)
        if is_dir and name in self.ignore_dirs:
            return True
        if not is_dir:
            _, ext = os.path.splitext(name)
            if ext.lower() in self.ignore_extensions:
                return True
        rel_path = os.path.relpath(path, self.root_dir)
        for pattern in self.gitignore_patterns:
            if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(name, pattern):
                return True
        return False

    def generate_folder_tree(self) -> str:
        tree_str = []
        for root, dirs, files in os.walk(self.root_dir):
            dirs[:] = [d for d in dirs if not self._is_ignored(os.path.join(root, d), is_dir=True)]
            level = root.replace(self.root_dir, '').count(os.sep)
            indent = ' ' * 4 * level
            folder_name = os.path.basename(root) if level > 0 else os.path.basename(self.root_dir)
            tree_str.append(f"{indent}📁 {folder_name}/")
            
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                file_path = os.path.join(root, f)
                if not self._is_ignored(file_path, is_dir=False):
                    tree_str.append(f"{subindent}📄 {f}")
        return '\n'.join(tree_str)

    def read_all_valid_files(self) -> dict:
        file_contents = {}
        for root, dirs, files in os.walk(self.root_dir):
            dirs[:] = [d for d in dirs if not self._is_ignored(os.path.join(root, d), is_dir=True)]
            for file in files:
                file_path = os.path.join(root, file)
                if self._is_ignored(file_path, is_dir=False):
                    continue
                rel_path = os.path.relpath(file_path, self.root_dir)
                
                # EDGE CASE: Skip empty files
                if os.path.getsize(file_path) == 0:
                    print(f"⚠️ Skipping empty file: {rel_path}")
                    continue
                    
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if content.strip():
                            file_contents[rel_path] = content
                except UnicodeDecodeError:
                    print(f"⚠️ Skipping binary/unreadable file: {rel_path}")
                    continue
        return file_contents