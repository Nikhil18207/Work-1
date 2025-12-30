"""
Extract content from PDF files for data analysis
"""

import sys
from pathlib import Path
import json
from datetime import datetime

try:
    import PyPDF2
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False


def extract_with_pdfplumber(pdf_path):
    """Extract text using pdfplumber (better for tables)"""
    if not HAS_PDFPLUMBER:
        return None
    
    extracted_data = {
        'source': str(pdf_path),
        'extraction_method': 'pdfplumber',
        'timestamp': datetime.now().isoformat(),
        'pages': []
    }
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_data = {
                    'page_number': page_num,
                    'text': page.extract_text(),
                    'tables': [],
                    'metadata': {
                        'width': page.width,
                        'height': page.height
                    }
                }
                
                # Extract tables if present
                tables = page.extract_tables()
                if tables:
                    for table_idx, table in enumerate(tables):
                        page_data['tables'].append({
                            'table_index': table_idx,
                            'rows': table
                        })
                
                extracted_data['pages'].append(page_data)
        
        return extracted_data
    except Exception as e:
        print(f"Error with pdfplumber: {e}")
        return None


def extract_with_pypdf2(pdf_path):
    """Extract text using PyPDF2 (basic extraction)"""
    if not HAS_PYPDF:
        return None
    
    extracted_data = {
        'source': str(pdf_path),
        'extraction_method': 'PyPDF2',
        'timestamp': datetime.now().isoformat(),
        'pages': []
    }
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            for page_num, page in enumerate(pdf_reader.pages, 1):
                text = page.extract_text()
                extracted_data['pages'].append({
                    'page_number': page_num,
                    'text': text,
                    'metadata': {
                        'author': pdf_reader.metadata.author if pdf_reader.metadata else None,
                        'creator': pdf_reader.metadata.creator if pdf_reader.metadata else None
                    }
                })
        
        return extracted_data
    except Exception as e:
        print(f"Error with PyPDF2: {e}")
        return None


def extract_pdf(pdf_path):
    """Extract content from PDF file"""
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        print(f"❌ File not found: {pdf_path}")
        return None
    
    if pdf_path.suffix.lower() != '.pdf':
        print(f"❌ Not a PDF file: {pdf_path}")
        return None
    
    print(f"\n📄 Extracting PDF: {pdf_path.name}")
    print(f"   Size: {pdf_path.stat().st_size / 1024:.1f} KB")
    
    # Try pdfplumber first (better for structured data)
    if HAS_PDFPLUMBER:
        print("   Using pdfplumber (better for tables and formatting)...")
        result = extract_with_pdfplumber(pdf_path)
        if result:
            return result
    
    # Fall back to PyPDF2
    if HAS_PYPDF:
        print("   Using PyPDF2...")
        result = extract_with_pypdf2(pdf_path)
        if result:
            return result
    
    print("\n❌ No PDF extraction libraries found!")
    print("   Install with: pip install pdfplumber PyPDF2")
    return None


def save_extracted_content(content, output_file=None):
    """Save extracted content to JSON"""
    if not content:
        return None
    
    if output_file is None:
        output_file = Path('data/extracted/pdf_content.json')
    
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(content, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Extracted content saved to: {output_path}")
    return output_path


def print_summary(content):
    """Print extraction summary"""
    if not content:
        return
    
    print(f"\n{'='*80}")
    print(f" EXTRACTION SUMMARY")
    print(f"{'='*80}")
    print(f"\nSource: {content.get('source')}")
    print(f"Method: {content.get('extraction_method')}")
    print(f"Pages: {len(content.get('pages', []))}")
    
    total_text = 0
    total_tables = 0
    
    for page in content.get('pages', []):
        text = page.get('text', '')
        if text:
            total_text += len(text)
        tables = page.get('tables', [])
        if tables:
            total_tables += len(tables)
    
    print(f"Total text characters: {total_text:,}")
    print(f"Total tables found: {total_tables}")
    
    print(f"\nFirst 500 characters from page 1:")
    first_page = content.get('pages', [{}])[0]
    text = first_page.get('text', '')[:500]
    print(f"\n{text}...")
    
    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    # Check if PDF path provided
    if len(sys.argv) < 2:
        print("Usage: python extract_pdf_content.py <pdf_file_path>")
        print("\nExample:")
        print('  python extract_pdf_content.py "c:\\path\\to\\file.pdf"')
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    
    # Extract content
    content = extract_pdf(pdf_file)
    
    if content:
        # Print summary
        print_summary(content)
        
        # Save to JSON
        output_file = save_extracted_content(content)
        
        print("📋 Content extracted and saved!")
        print("\n✨ Next steps:")
        print("   1. Review the extracted content")
        print("   2. Import into coaching system for analysis")
        print("   3. Use for supplier/tariff data updates")
    else:
        print("\n❌ Failed to extract PDF content")
        print("\nTroubleshooting:")
        print("   1. Verify the file path is correct")
        print("   2. Install PDF libraries: pip install pdfplumber PyPDF2")
        print("   3. Ensure the PDF is readable (not encrypted)")
