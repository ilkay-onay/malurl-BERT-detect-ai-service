import os
from pathlib import Path

# ==========================================
# CONFIGURATION: What to include/exclude
# ==========================================
# Folders to completely skip
IGNORE_DIRS = {
    'venv', '.venv', 'env', '__pycache__', '.git', 
    'outputs', 'logs', 'plots', 'data', 'build', 'dist', 
    '.ipynb_checkpoints', '.vscode'
}

# Only map these file types
INCLUDE_EXTENSIONS = {'.py', '.txt', '.md', '.yml', '.yaml', '.sh'}

# Specific files to ignore
IGNORE_FILES = {'map_codebase.py', 'online-valid.json', 'processed_dataset.csv'}

def generate_tree(directory, prefix=""):
    """Recursive function to build a text-based file tree."""
    tree = ""
    entries = sorted(os.scandir(directory), key=lambda e: (e.is_file(), e.name))
    entries = [e for e in entries if e.name not in IGNORE_DIRS and e.name not in IGNORE_FILES]
    
    for i, entry in enumerate(entries):
        connector = "└── " if i == len(entries) - 1 else "├── "
        if entry.is_dir():
            tree += f"{prefix}{connector}{entry.name}/\n"
            tree += generate_tree(entry.path, prefix + ("    " if i == len(entries) - 1 else "│   "))
        else:
            if Path(entry.name).suffix in INCLUDE_EXTENSIONS:
                tree += f"{prefix}{connector}{entry.name}\n"
    return tree

def map_project(output_file="CODEBASE_MAP.txt"):
    root_dir = os.getcwd()
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("============================================================\n")
        f.write(f"PROJECT MAP: {os.path.basename(root_dir)}\n")
        f.write("============================================================\n\n")
        
        # 1. Write the Tree structure
        f.write("DIRECTORY STRUCTURE:\n")
        f.write(".\n")
        f.write(generate_tree(root_dir))
        f.write("\n" + "="*60 + "\n\n")
        
        # 2. Iterate and write file contents
        for root, dirs, files in os.walk(root_dir):
            # Filter directories
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            
            for file in sorted(files):
                if Path(file).suffix in INCLUDE_EXTENSIONS and file not in IGNORE_FILES:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, root_dir)
                    
                    f.write(f"\nFILE: {rel_path}\n")
                    f.write("-" * len(f"FILE: {rel_path}") + "\n")
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as src:
                            f.write(src.read())
                    except Exception as e:
                        f.write(f"[Error reading file: {e}]")
                    
                    f.write("\n\n" + "#" * 40 + "\n")

    print(f"✅ Success! Relevant codebase mapped to: {output_file}")

if __name__ == "__main__":
    map_project()