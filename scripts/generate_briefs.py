#!/usr/bin/env python
"""
UNIFIED BRIEF GENERATOR
========================
ONE script for ALL industries. Just pass the category you want.

Usage:
    python generate_briefs.py "Raw Materials - Steel"
    python generate_briefs.py "IT Hardware"
    python generate_briefs.py "Pharmaceuticals"
    python generate_briefs.py "Logistics Services"
    python generate_briefs.py "Marketing Services"
    python generate_briefs.py  # (interactive mode - lists all available categories)
"""

import sys
from pathlib import Path

# Add project root to path (go up one level from scripts/)
root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from backend.engines.leadership_brief_generator import LeadershipBriefGenerator
from backend.engines.docx_exporter import DOCXExporter
from backend.engines.data_loader import DataLoader


def get_available_categories():
    """Get all available categories from spend_data.csv"""
    loader = DataLoader()
    spend_df = loader.load_spend_data()
    
    # Get unique categories with their client IDs
    category_client = spend_df.groupby('Category')['Client_ID'].first().to_dict()
    return category_client


def generate_briefs_for_category(category: str, client_id: str = None):
    """
    Generate DOCX briefs for ANY category
    
    Args:
        category: Product category (e.g., "Raw Materials - Steel", "IT Hardware", etc.)
        client_id: Optional client ID. If not provided, auto-detects from data.
    """
    print("\n" + "=" * 70)
    print(f"  GENERATING BRIEFS FOR: {category}")
    print("=" * 70)
    
    # Auto-detect client ID if not provided
    if not client_id:
        loader = DataLoader()
        spend_df = loader.load_spend_data()
        category_clients = spend_df[spend_df['Category'] == category]['Client_ID'].unique()
        
        if len(category_clients) == 0:
            print(f"\n❌ ERROR: No data found for category '{category}'")
            print("\nAvailable categories:")
            for cat in spend_df['Category'].unique():
                print(f"   • {cat}")
            return None
        
        client_id = category_clients[0]
        print(f"\n📋 Auto-detected Client ID: {client_id}")
    
    # Initialize generators
    print("\n⏳ Initializing generators...")
    generator = LeadershipBriefGenerator()
    exporter = DOCXExporter()
    
    # Generate briefs
    print(f"⏳ Generating briefs for '{category}'...")
    briefs = generator.generate_both_briefs(client_id=client_id, category=category)
    
    # Check if briefs were generated
    incumbent = briefs.get('incumbent_concentration_brief', {})
    regional = briefs.get('regional_concentration_brief', {})
    
    if incumbent.get('total_spend', 0) == 0:
        print(f"\n❌ ERROR: No spend data found for {category}")
        return None
    
    # Display summary
    print(f"\n📊 BRIEF SUMMARY:")
    print(f"   Category: {category}")
    print(f"   Total Spend: ${incumbent.get('total_spend', 0):,.0f}")
    print(f"   Dominant Supplier: {incumbent.get('current_state', {}).get('dominant_supplier', 'N/A')}")
    print(f"   Concentration: {incumbent.get('current_state', {}).get('spend_share_pct', 0):.1f}%")
    
    # Export to DOCX
    print(f"\n⏳ Exporting to DOCX...")
    docx_files = exporter.export_both_briefs(briefs, export_pdf=False)
    
    print(f"\n✅ SUCCESS! Files generated:")
    for brief_type, filepath in docx_files.items():
        filename = Path(filepath).name
        print(f"   📄 {brief_type}: {filename}")
    
    print(f"\n📁 Output directory: outputs/briefs/")
    print("=" * 70 + "\n")
    
    return docx_files


def interactive_mode():
    """Interactive mode - let user select category"""
    print("\n" + "=" * 70)
    print("  UNIFIED BRIEF GENERATOR - Interactive Mode")
    print("=" * 70)
    
    # Get available categories
    category_client = get_available_categories()
    
    print("\n📋 Available Categories:\n")
    categories = list(category_client.keys())
    for i, cat in enumerate(categories, 1):
        client = category_client[cat]
        print(f"   {i:2d}. {cat} (Client: {client})")
    
    print(f"\n   Enter number (1-{len(categories)}) or category name:")
    
    try:
        user_input = input("   > ").strip()
        
        # Check if numeric
        if user_input.isdigit():
            idx = int(user_input) - 1
            if 0 <= idx < len(categories):
                selected_category = categories[idx]
            else:
                print(f"❌ Invalid selection. Please enter 1-{len(categories)}")
                return
        else:
            # Find matching category
            matches = [c for c in categories if user_input.lower() in c.lower()]
            if len(matches) == 1:
                selected_category = matches[0]
            elif len(matches) > 1:
                print(f"Multiple matches found: {matches}")
                print("Please be more specific.")
                return
            else:
                print(f"❌ Category '{user_input}' not found.")
                return
        
        # Generate briefs
        client_id = category_client[selected_category]
        generate_briefs_for_category(selected_category, client_id)
        
    except KeyboardInterrupt:
        print("\n\nCancelled.")


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        # Command line mode - category passed as argument
        category = " ".join(sys.argv[1:])
        generate_briefs_for_category(category)
    else:
        # Interactive mode
        interactive_mode()


if __name__ == "__main__":
    main()
