"""
Script to remove emojis and clean up comments from all Python files
"""
import os
import re
from pathlib import Path

def remove_emojis(text):
    """Remove all emojis from text"""
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001F900-\U0001F9FF"  # supplemental symbols
        "\U0001FA70-\U0001FAFF"
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub('', text)

def clean_python_file(filepath):
    """Clean a single Python file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Remove emojis
        content = remove_emojis(content)
        
        # Remove excessive comment decorations like ===, ---, etc.
        content = re.sub(r'^\s*#\s*[=\-*]{10,}\s*$', '', content, flags=re.MULTILINE)
        
        # Remove bullet points from comments
        content = content.replace('-', '-')
        
        # Only write if changed
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def main():
    """Clean all Python files in the project"""
    project_root = Path(__file__).parent.parent
    
    # Find all Python files, excluding venv
    python_files = []
    for root, dirs, files in os.walk(project_root):
        # Skip virtual environment
        if 'Beroe_Env' in root or '__pycache__' in root:
            continue
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(Path(root) / file)
    
    print(f"Found {len(python_files)} Python files to clean")
    
    cleaned_count = 0
    for filepath in python_files:
        if clean_python_file(filepath):
            cleaned_count += 1
            print(f"Cleaned: {filepath.relative_to(project_root)}")
    
    print(f"\nCleaned {cleaned_count} out of {len(python_files)} files")

if __name__ == "__main__":
    main()
