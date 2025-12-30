"""
Demo: All Export Formats
Shows TXT, MD, HTML, and DOCX exports
"""

import sys
from pathlib import Path

root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from backend.engines.leadership_brief_generator import LeadershipBriefGenerator
from backend.engines.text_exporter import TextExporter

try:
    from backend.engines.docx_exporter import DOCXExporter
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


def main():
    print("\n" + "=" * 80)
    print("LEADERSHIP BRIEF EXPORT - ALL FORMATS")
    print("=" * 80)
    
    print("\n📊 Generating briefs for Client C001, Category: Rice Bran Oil...")
    
    # Generate briefs
    generator = LeadershipBriefGenerator()
    briefs = generator.generate_both_briefs(
        client_id='C001',
        category='Rice Bran Oil'
    )
    
    print("✅ Briefs generated successfully!")
    
    # Export to text formats
    print("\n" + "=" * 80)
    print("EXPORTING TO TEXT FORMATS")
    print("=" * 80)
    
    exporter = TextExporter()
    
    # TXT format
    print("\n📄 Exporting to TXT (Plain Text)...")
    txt_files = exporter.export_both_briefs(briefs, format='txt')
    print(f"   ✅ Incumbent: {txt_files['incumbent_concentration']}")
    print(f"   ✅ Regional:  {txt_files['regional_concentration']}")
    
    # Markdown format
    print("\n📝 Exporting to MD (Markdown)...")
    md_files = exporter.export_both_briefs(briefs, format='md')
    print(f"   ✅ Incumbent: {md_files['incumbent_concentration']}")
    print(f"   ✅ Regional:  {md_files['regional_concentration']}")
    
    # HTML format
    print("\n🌐 Exporting to HTML...")
    html_files = exporter.export_both_briefs(briefs, format='html')
    print(f"   ✅ Incumbent: {html_files['incumbent_concentration']}")
    print(f"   ✅ Regional:  {html_files['regional_concentration']}")
    
    # DOCX format (if available)
    if DOCX_AVAILABLE:
        print("\n📄 Exporting to DOCX (Word Document)...")
        try:
            from backend.engines.docx_exporter import DOCXExporter
            docx_exporter = DOCXExporter()
            docx_files = docx_exporter.export_both_briefs(briefs)
            print(f"   ✅ Incumbent: {docx_files['incumbent_concentration']}")
            print(f"   ✅ Regional:  {docx_files['regional_concentration']}")
        except Exception as e:
            print(f"   ⚠️  DOCX export failed: {e}")
    else:
        print("\n⚠️  DOCX export skipped (python-docx not installed)")
        print("   Install with: pip install python-docx")
    
    # Summary
    print("\n" + "=" * 80)
    print("✅ EXPORT COMPLETE!")
    print("=" * 80)
    
    print("\n📁 All files saved to: outputs/briefs/")
    print("\n📊 Available Formats:")
    print("   ✅ TXT  - Plain text, easy to read in any text editor")
    print("   ✅ MD   - Markdown, great for GitHub/documentation")
    print("   ✅ HTML - Web format, open in any browser")
    if DOCX_AVAILABLE:
        print("   ✅ DOCX - Microsoft Word format")
    
    print("\n💡 You can now:")
    print("   • Open .txt files in Notepad/VS Code")
    print("   • Open .md files in VS Code/GitHub")
    print("   • Open .html files in your browser")
    if DOCX_AVAILABLE:
        print("   • Open .docx files in Microsoft Word")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
