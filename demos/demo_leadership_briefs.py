"""
Demo: Generate Leadership Briefs in Markdown Format Only
"""

import sys
from pathlib import Path

root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from backend.engines.leadership_brief_generator import LeadershipBriefGenerator
from backend.engines.text_exporter import TextExporter


def main():
    print("\n" + "=" * 80)
    print("LEADERSHIP BRIEF GENERATION - MARKDOWN FORMAT")
    print("=" * 80)
    
    print("\n📊 Generating briefs for Client C001, Category: Rice Bran Oil...")
    
    # Generate briefs
    generator = LeadershipBriefGenerator()
    briefs = generator.generate_both_briefs(
        client_id='C001',
        category='Rice Bran Oil'
    )
    
    print("✅ Briefs generated successfully!")
    
    # Export to Markdown only
    print("\n" + "=" * 80)
    print("EXPORTING TO MARKDOWN FORMAT")
    print("=" * 80)
    
    exporter = TextExporter()
    
    print("\n📝 Exporting to MD (Markdown)...")
    md_files = exporter.export_both_briefs(briefs, format='md')
    print(f"   ✅ Incumbent: {md_files['incumbent_concentration']}")
    print(f"   ✅ Regional:  {md_files['regional_concentration']}")
    
    # Summary
    print("\n" + "=" * 80)
    print("✅ EXPORT COMPLETE!")
    print("=" * 80)
    
    print("\n📁 Files saved to: outputs/briefs/")
    print("\n📊 Format: Markdown (.md)")
    print("   • Great for GitHub/documentation")
    print("   • Easy to read in VS Code")
    print("   • Can be converted to other formats if needed")
    
    print("\n💡 View the files:")
    print("   • Open in VS Code with Markdown preview")
    print("   • Push to GitHub for beautiful rendering")
    print("   • Convert to PDF/DOCX if needed later")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
