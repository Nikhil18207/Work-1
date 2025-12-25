"""
Data Switcher - Switch between Food-Only and Multi-Industry Data
"""

import shutil
import os
from pathlib import Path

def switch_to_multi_industry():
    """Switch to comprehensive multi-industry data"""
    print("\n" + "="*80)
    print("🌐 SWITCHING TO MULTI-INDUSTRY DATA")
    print("="*80)
    
    data_dir = Path("data/structured")
    
    # Backup original files
    print("\n📦 Backing up original food data...")
    files_to_backup = [
        "spend_data.csv",
        "client_master.csv",
        "supplier_master.csv"
    ]
    
    for file in files_to_backup:
        original = data_dir / file
        backup = data_dir / f"{file}.food_backup"
        if original.exists():
            shutil.copy(original, backup)
            print(f"   ✓ Backed up: {file} → {file}.food_backup")
    
    # Copy multi-industry files
    print("\n🔄 Activating multi-industry data...")
    files_to_copy = [
        ("spend_data_multi_industry.csv", "spend_data.csv"),
        ("client_master_multi_industry.csv", "client_master.csv"),
        ("supplier_master_multi_industry.csv", "supplier_master.csv")
    ]
    
    for source, dest in files_to_copy:
        source_file = data_dir / source
        dest_file = data_dir / dest
        if source_file.exists():
            shutil.copy(source_file, dest_file)
            print(f"   ✓ Activated: {source} → {dest}")
        else:
            print(f"   ❌ Missing: {source}")
    
    print("\n✅ MULTI-INDUSTRY DATA ACTIVATED!")
    print("\nYour system now includes:")
    print("   • Food & Beverage (Edible Oils)")
    print("   • IT Hardware (Dell, HP, Lenovo, Apple, Cisco)")
    print("   • Cloud Services (AWS, Azure, Google Cloud)")
    print("   • Software (Oracle, SAP, IBM, Salesforce)")
    print("   • Manufacturing (Steel, Aluminum, Copper, Plastics)")
    print("   • Equipment (Siemens, ABB, Caterpillar, Komatsu)")
    print("   • Healthcare (Pfizer, J&J, Medtronic, Roche)")
    print("   • Construction (Cemex, LafargeHolcim, Hilti)")
    print("   • Marketing (WPP, Omnicom, Google Ads, McKinsey)")
    print("   • Office Supplies (Staples, Steelcase, Herman Miller)")
    print("   • Energy (NextEra, Vestas, First Solar)")
    print("   • Logistics (DHL, FedEx, UPS, Maersk)")
    print("   • Telecommunications (Verizon, AT&T, Vodafone)")
    print("   • Professional Services (PwC, EY, KPMG, Baker McKenzie)")
    print("   • HR Services (ADP, Robert Half, Skillsoft)")
    print("\n📊 Total Data:")
    print("   • 15 Clients across different industries")
    print("   • 100+ Suppliers globally")
    print("   • 180+ Transactions")
    print("   • 15+ Procurement Categories")
    print("\n" + "="*80)
    print("🚀 Ready to use! Run: python main.py")
    print("="*80 + "\n")


def switch_to_food_only():
    """Switch back to food-only data"""
    print("\n" + "="*80)
    print("🍽️ SWITCHING TO FOOD-ONLY DATA")
    print("="*80)
    
    data_dir = Path("data/structured")
    
    # Restore from backup
    print("\n🔄 Restoring original food data...")
    files_to_restore = [
        "spend_data.csv",
        "client_master.csv",
        "supplier_master.csv"
    ]
    
    for file in files_to_restore:
        backup = data_dir / f"{file}.food_backup"
        original = data_dir / file
        if backup.exists():
            shutil.copy(backup, original)
            print(f"   ✓ Restored: {file}")
        else:
            print(f"   ❌ No backup found for: {file}")
    
    print("\n✅ FOOD-ONLY DATA RESTORED!")
    print("\nYour system now includes:")
    print("   • Rice Bran Oil procurement data")
    print("   • Original suppliers (Malaysia-focused)")
    print("   • Original client (C001)")
    print("\n" + "="*80)
    print("🚀 Ready to use! Run: python main.py")
    print("="*80 + "\n")


if __name__ == "__main__":
    import sys
    
    print("\n" + "="*80)
    print("📊 DATA SWITCHER - Choose Your Dataset")
    print("="*80)
    print("\n1. Multi-Industry Data (15+ sectors, 100+ suppliers, 180+ transactions)")
    print("2. Food-Only Data (Original Rice Bran Oil data)")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1/2/3): ").strip()
    
    if choice == "1":
        switch_to_multi_industry()
    elif choice == "2":
        switch_to_food_only()
    elif choice == "3":
        print("\n👋 Goodbye!\n")
        sys.exit(0)
    else:
        print("\n❌ Invalid choice. Please run again and select 1, 2, or 3.\n")
