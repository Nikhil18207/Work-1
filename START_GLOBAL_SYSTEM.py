#!/usr/bin/env python
"""
Global Procurement LLM System - Quick Start
Launches the complete analysis platform with document upload capability
"""

import sys
import os
from pathlib import Path
import subprocess

def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = {
        'streamlit': 'streamlit',
        'pandas': 'pandas',
        'openpyxl': 'openpyxl',
        'python-docx': 'docx',  # Note: imports as 'docx'
        'reportlab': 'reportlab',
        'PyPDF2': 'PyPDF2',
        'numpy': 'numpy'
    }
    
    print("🔍 Checking dependencies...")
    missing = []
    
    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name} - MISSING")
            missing.append(package_name)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("Install with: pip install -r requirements_enhanced.txt")
        return False
    
    print("\n✅ All dependencies installed!")
    return True

def check_modules():
    """Check if all analysis engine modules are present"""
    required_modules = [
        'backend/engines/document_parser.py',
        'backend/engines/leadership_brief_generator.py',
        'backend/engines/docx_exporter.py',
        'backend/engines/pdf_exporter.py',
        'backend/engines/excel_exporter.py',
        'backend/engines/risk_analyzer.py',
        'backend/engines/market_intelligence.py',
        'backend/engines/tco_calculator.py',
        'backend/engines/compliance_analyzer.py',
        'backend/engines/implementation_roadmap.py',
        'backend/engines/scenario_analyzer.py'
    ]
    
    print("\n🔍 Checking analysis modules...")
    missing = []
    
    for module in required_modules:
        if Path(module).exists():
            print(f"✅ {module}")
        else:
            print(f"❌ {module} - MISSING")
            missing.append(module)
    
    if missing:
        print(f"\n⚠️  Missing modules: {', '.join(missing)}")
        print("Ensure all engine files are in backend/engines/")
        return False
    
    print("\n✅ All analysis modules present!")
    return True

def launch_app():
    """Launch the Streamlit application"""
    print("\n" + "="*60)
    print("🌍 Global Procurement LLM System")
    print("="*60)
    print("\n📱 Launching web interface...")
    print("🌐 Opening: http://localhost:8501\n")
    
    try:
        subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'global_procurement_app.py'])
    except KeyboardInterrupt:
        print("\n\n👋 Application closed. Thank you for using Global Procurement LLM!")
    except Exception as e:
        print(f"\n❌ Error launching application: {str(e)}")
        print("\nManual launch:")
        print("  streamlit run global_procurement_app.py")

def main():
    """Main entry point"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║      🌍 Global Procurement LLM System - Quick Start          ║
    ║                                                              ║
    ║   Comprehensive procurement analysis for ANY industry        ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Setup incomplete. Please install missing packages.")
        return False
    
    # Check modules
    if not check_modules():
        print("\n❌ Setup incomplete. Please verify all modules are present.")
        return False
    
    # All checks passed
    print("\n" + "="*60)
    print("✅ System ready! All dependencies and modules present")
    print("="*60)
    
    # Launch
    launch_app()
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
