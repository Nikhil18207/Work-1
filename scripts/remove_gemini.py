"""
Script to remove Google Gemini dependencies from the codebase
Since we're only using OpenAI, this removes all Gemini imports and code
"""
import re
from pathlib import Path

def remove_gemini_from_rag_engine():
    """Remove Gemini from rag_engine.py"""
    filepath = Path("backend/engines/rag_engine.py")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove Gemini import block
    content = re.sub(
        r'try:\s+import google\.generativeai as genai\s+except ImportError:\s+genai = None\s+',
        '',
        content,
        flags=re.MULTILINE | re.DOTALL
    )
    
    # Remove Gemini initialization code (lines 60-71)
    content = re.sub(
        r'if self\.provider == "google":\s+.*?else:',
        'if self.provider == "openai":',
        content,
        flags=re.DOTALL
    )
    
    # Remove Gemini generation code
    content = re.sub(
        r'if self\.provider == "google":.*?else:\s+# For OpenAI',
        '# For OpenAI',
        content,
        flags=re.DOTALL
    )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Cleaned: {filepath}")

def remove_gemini_from_llm_engine():
    """Remove Gemini from llm_engine.py"""
    filepath = Path("backend/engines/llm_engine.py")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Remove lines containing Gemini imports and references
    cleaned_lines = []
    skip_until = None
    
    for i, line in enumerate(lines):
        # Skip Gemini import
        if 'import google.generativeai' in line:
            continue
        # Skip GEMINI_API_KEY references
        if 'GEMINI_API_KEY' in line:
            continue
        # Skip Gemini-related if blocks
        if 'if self.provider == LLMProvider.GEMINI' in line:
            skip_until = 'else:'
            continue
        if skip_until and skip_until in line:
            skip_until = None
            continue
        if skip_until:
            continue
            
        cleaned_lines.append(line)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(cleaned_lines)
    
    print(f"Cleaned: {filepath}")

def remove_gemini_from_vector_store():
    """Remove Gemini from vector_store_manager.py"""
    filepath = Path("backend/engines/vector_store_manager.py")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace GEMINI_API_KEY references
    content = content.replace(
        'self.api_key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")',
        'self.api_key = api_key or os.getenv("OPENAI_API_KEY")'
    )
    
    # Remove GoogleGenerativeAIEmbeddings import
    content = re.sub(
        r'try:\s+from langchain_google_genai import GoogleGenerativeAIEmbeddings\s+except ImportError:\s+GoogleGenerativeAIEmbeddings = None\s+',
        '',
        content,
        flags=re.MULTILINE | re.DOTALL
    )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Cleaned: {filepath}")

def main():
    """Remove all Gemini dependencies"""
    print("Removing Google Gemini dependencies...")
    print("="*60)
    
    remove_gemini_from_rag_engine()
    remove_gemini_from_llm_engine()
    remove_gemini_from_vector_store()
    
    print("="*60)
    print("Done! All Gemini dependencies removed.")
    print("The system now uses OpenAI exclusively.")

if __name__ == "__main__":
    main()
