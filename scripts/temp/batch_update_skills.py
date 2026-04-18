import os
import re

SKILLS_DIR = r"d:\Python\Mathproject\skills"

def batch_update_skills():
    count = 0
    for filename in os.listdir(SKILLS_DIR):
        if not filename.endswith(".py") or filename == "__init__.py":
            continue
            
        filepath = os.path.join(SKILLS_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        original_content = content
        
        # Pattern 1: Update 'Correct' return
        # Matches: return {'correct': True, 'result': 'Correct!'} (or similar variants)
        # Replaces with: return {'correct': True, 'result': '正確！'}
        content = re.sub(
            r"return\s+\{\s*['\"]correct['\"]\s*:\s*True\s*,\s*['\"]result['\"]\s*:\s*['\"].*?['\"]\s*\}",
            "return {'correct': True, 'result': '正確！'}",
            content,
            flags=re.IGNORECASE
        )

        # Pattern 2: Update 'Incorrect' return
        # Matches: return {'correct': False, 'result': ...}
        # Replaces with: Standard V10.3.1 Error format
        content = re.sub(
            r"return\s+\{\s*['\"]correct['\"]\s*:\s*False\s*,\s*['\"]result['\"]\s*:\s*.*?\s*\}",
            "return {'correct': False, 'result': r'答案錯誤。正確答案為：{ans}'.replace('{ans}', str(correct_answer))}",
            content,
            flags=re.IGNORECASE | re.DOTALL
        )

        if content != original_content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Updated: {filename}")
            count += 1
            
    print(f"Total files updated: {count}")

if __name__ == "__main__":
    batch_update_skills()
