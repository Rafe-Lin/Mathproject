
import os
import re
from datetime import datetime

SKILLS_DIR = r'd:\Python\Mathproject\skills'
TARGET_VERSION = "V2.0"
TARGET_DATE = "2026-01-13"
MAINTAINER = "Math AI Project Team"

HEADER_TEMPLATE = """# -*- coding: utf-8 -*-
\"\"\"
=============================================================================
模組名稱 (Module Name): skills/{filename}
功能說明 (Description): 本模組負責自動生成「{skill_name}」相關的數學練習題，包含題目生成 (generate) 與答案檢查 (check) 功能。
執行語法 (Usage): 由系統調用
版本資訊 (Version): {version}
更新日期 (Date): {date}
維護團隊 (Maintainer): {maintainer}
=============================================================================
\"\"\"
"""

def update_file_header(filepath):
    filename = os.path.basename(filepath)
    skill_name = os.path.splitext(filename)[0]
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if header exists (look for the separator line)
    header_pattern = re.compile(r'={70,}')
    
    if header_pattern.search(content):
        # Header exists, update Version and Date
        print(f"Updating existing header for: {filename}")
        
        # Update Version
        content = re.sub(r'版本資訊 \(Version\): .*', f'版本資訊 (Version): {TARGET_VERSION}', content)
        # Update Date (Optional, but good for consistency)
        content = re.sub(r'更新日期 \(Date\): .*', f'更新日期 (Date): {TARGET_DATE}', content)
        
    else:
        # Header missing, prepend new header
        print(f"Adding new header to: {filename}")
        
        # Remove existing encoding declaration if simple
        if content.startswith('# -*- coding: utf-8 -*-'):
            content = content.replace('# -*- coding: utf-8 -*-\n', '', 1)
        
        new_header = HEADER_TEMPLATE.format(
            filename=filename,
            skill_name=skill_name,
            version=TARGET_VERSION,
            date=TARGET_DATE,
            maintainer=MAINTAINER
        )
        content = new_header + content

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    if not os.path.exists(SKILLS_DIR):
        print(f"Directory not found: {SKILLS_DIR}")
        return

    count = 0
    for filename in os.listdir(SKILLS_DIR):
        if filename.endswith('.py') and filename != '__init__.py':
            filepath = os.path.join(SKILLS_DIR, filename)
            try:
                update_file_header(filepath)
                count += 1
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    print(f"Processed {count} files.")

if __name__ == "__main__":
    main()
