import sys
import os
from src.agents import ReadmeAgent

def main():
    print("🚀 Initializing Epoch X Nasiko README Agent...")
    
    # Allow passing a target directory via command line, default to current directory
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    target_dir_abs = os.path.abspath(target_dir)
    
    if not os.path.exists(target_dir_abs):
        print(f"❌ Error: The directory '{target_dir_abs}' does not exist.")
        sys.exit(1)
        
    try:
        agent = ReadmeAgent(target_dir=target_dir_abs)
        agent.generate()
    except ValueError as ve:
        print(f"⚙️ Configuration Error: {ve}")
    except Exception as e:
        print(f"💥 An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()