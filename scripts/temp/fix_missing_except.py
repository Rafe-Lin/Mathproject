import os
import glob
import re

SKILLS_DIR = r"d:\Python\Mathproject\skills"

def fix_missing_except(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    in_check = False
    has_try = False
    has_except = False
    try_indent = ""
    check_indent = ""
    
    fail_return_template = 'return {"correct": False, "result": r"""答案錯誤。正確答案為：{ans}""".replace("{ans}", str(correct_answer))}'

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        if stripped.startswith("def check(") and ":" in stripped:
            in_check = True
            has_try = False
            has_except = False
            check_indent = line[:line.find("def")]
            new_lines.append(line)
            i += 1
            continue
            
        if in_check:
            if stripped and not stripped.startswith("#"):
                current_indent = line[:len(line) - len(stripped)]
                if len(current_indent) <= len(check_indent):
                    if has_try and not has_except:
                        new_lines.append(f"{try_indent}except:\n")
                        new_lines.append(f"{try_indent}    {fail_return_template}\n")
                        print(f"Fixed missing except in {filepath}")
                    
                    in_check = False
                    new_lines.append(line)
                    i += 1
                    continue

            if stripped.startswith("try:"):
                has_try = True
                try_indent = line[:line.find("try")]
            
            if stripped.startswith("except") and stripped.endswith(":"):
                has_except = True
                
        new_lines.append(line)
        i += 1

    if in_check and has_try and not has_except:
         new_lines.append(f"{try_indent}except:\n")
         new_lines.append(f"{try_indent}    {fail_return_template}\n")
         print(f"Fixed missing except in {filepath} (at EOF)")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

def main():
    files = glob.glob(os.path.join(SKILLS_DIR, "*.py"))
    for f in files:
        fix_missing_except(f)

if __name__ == "__main__":
    main()
