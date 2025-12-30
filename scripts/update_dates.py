"""
Update all 2024 references to January 2026
"""

import re

def update_file_dates(filepath):
    """Update 2024 to January 2026 in a file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Only replace in string literals and comments
        # Replace common patterns
        patterns = [
            (r'"2024"', '"January 2026"'),
            (r"'2024'", "'January 2026'"),
            (r'Spend 2024:', 'Spend January 2026:'),
            (r'2024 Original', 'January 2026 Original'),
            (r'Original 2024', 'Original January 2026'),
            (r'\(2024\)', '(January 2026)'),
            (r'in 2024', 'in January 2026'),
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Updated: {filepath}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating {filepath}: {e}")
        return False


# Update files
files_to_update = [
    'backend/engines/text_exporter.py',
    'backend/engines/docx_exporter.py',
]

print("Updating date references from 2024 to January 2026...")
print("=" * 60)

for filepath in files_to_update:
    update_file_dates(filepath)

print("=" * 60)
print("✅ All files updated!")
