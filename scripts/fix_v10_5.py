import os
import re
import glob

SKILLS_DIR = r"d:\Python\Mathproject\skills"

# new patch content
PATCH_CONTENT = r"""
# [Auto-Injected Patch v10.4] Universal Return, Linebreak & Chinese Fixer
def _patch_all_returns(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        if func.__name__ == "check" and isinstance(res, bool):
            return {"correct": res, "result": "正確！" if res else "答案錯誤"}
        if isinstance(res, dict):
            if "question_text" in res and isinstance(res["question_text"], str):
                res["question_text"] = res["question_text"].replace("\\n", "\n")
            if func.__name__ == "check" and "result" in res:
                msg = str(res["result"]).lower()
                if any(w in msg for w in ["correct", "right", "success"]): res["result"] = "正確！"
                elif any(w in msg for w in ["incorrect", "wrong", "error"]):
                    if "正確答案" not in res["result"]: res["result"] = "答案錯誤"
            if "answer" not in res and "correct_answer" in res: res["answer"] = res["correct_answer"]
            if "answer" in res: res["answer"] = str(res["answer"])
            if "image_base64" not in res: res["image_base64"] = ""
        return res
    return wrapper
import sys
for _name, _func in list(globals().items()):
    if callable(_func) and (_name.startswith("generate") or _name == "check"):
        globals()[_name] = _patch_all_returns(_func)
"""

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    
    lines = content.split('\n')
    new_lines = []
    
    # 2. Fix Font Settings (Regex on full content is fine, but line-by-line is safer/cleaner)
    # Actually, let's just process line by line for everything related to logic
    
    canonical_return = 'return {"correct": False, "result": r"""答案錯誤。正確答案為：{ans}""".replace("{ans}", str(correct_answer))}'
    font_fix = "plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Arial Unicode MS', 'sans-serif']"

    for line in lines:
        stripped = line.strip()
        
        # Aggressive cleaning of the return line
        if 'r"""答案錯誤' in line and 'return' in line:
            # Preserve indentation
            indent = line[:line.find('return')]
            new_lines.append(indent + canonical_return)
            continue
            
        # Fix Font
        if "plt.rcParams['font.sans-serif']" in line and "=" in line:
            new_lines.append(font_fix)
            continue
            
        # Fix the None check return
        if 'if user_answer is None' in line and 'return' in line:
            # This might be on one line or two.
            # If it's on one line: if user_answer is None: return ...
            # We enforce the return part.
            indent = line[:line.find('if')]
            # if the return is on the same line
            if 'return' in line:
                new_lines.append(indent + f'if user_answer is None: {canonical_return}')
                continue
            # If split lines, we might miss it. But usually it's one line in these files.
            
        new_lines.append(line)
    
    content = '\n'.join(new_lines)

    # 4. Update Patch
    # Find where the patch starts. It usually starts with comments like:
    # # [Auto-Injected Patch...
    # or
    # def _patch_all_returns(func):
    
    patch_start_regex = r"(# \[Auto-Injected Patch.*?|def _patch_all_returns\(func\):)"
    match = re.search(patch_start_regex, content, re.DOTALL)
    
    if match:
        # Truncate content before the match
        content = content[:match.start()]
        # Add new patch
        content = content.strip() + "\n\n" + PATCH_CONTENT.strip() + "\n"
    else:
        # If no patch found, just append (unlikely for these files but safe backup)
        content = content.strip() + "\n\n" + PATCH_CONTENT.strip() + "\n"

    # Double check for the header comment of patch appearing twice? No, we truncated.

    if content != original_content:
        print(f"Fixing {filepath}...")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    else:
        print(f"No changes for {filepath}")
        return False

def main():
    files = glob.glob(os.path.join(SKILLS_DIR, "*.py"))
    print(f"Found {len(files)} files.")
    count = 0
    for f in files:
        if fix_file(f):
            count += 1
    print(f"Fixed {count} files.")

if __name__ == "__main__":
    main()
