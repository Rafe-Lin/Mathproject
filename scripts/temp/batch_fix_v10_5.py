import os
import re

SKILLS_DIR = r"d:\Python\Mathproject\skills"

# V10.4 Universal Patch Code (Standard V10.5 version)
V10_4_PATCH = r'''
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
                if any(w in msg for w in ["correct", "right"]): res["result"] = "正確！"
                elif any(w in msg for w in ["incorrect", "wrong"]):
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
'''

def batch_fix_v10_5():
    count = 0
    for filename in os.listdir(SKILLS_DIR):
        if not filename.endswith(".py") or filename == "__init__.py":
            continue
            
        filepath = os.path.join(SKILLS_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        original_content = content
        
        # 1. Matplotlib Font Fix (Double Quotes Strict)
        # Matches: Any font.sans-serif setting and replaces with the correct one
        content = re.sub(
            r"matplotlib\.rcParams\s*\[\s*['\"]font\.sans-serif['\"]\s*\]\s*=\s*\[.*?\]",
            'matplotlib.rcParams["font.sans-serif"] = ["Microsoft JhengHei"]',
            content,
            flags=re.IGNORECASE
        )

        # 2. Repair Correct Return
        # Replaces any existing return {"correct": True... line
        content = re.sub(
            r"return\s+\{\s*['\"]correct['\"]\s*:\s*True\s*,\s*['\"]result['\"]\s*:\s*['\"].*?['\"]\s*\}",
            'return {"correct": True, "result": "正確！"}',
            content,
            flags=re.IGNORECASE
        )

        # 3. Surgical Repair for Incorrect Return (V10.5 Cleanup)
        # This regex matches the corrupted line often seen: 
        # return {"correct": False, "result": r"""..."""}'.replace(...)
        # And replaces it with the clean version.
        # It's better to match the whole line pattern roughly and replace it.
        incorrect_pattern = r'return\s+\{\s*[\'"]correct[\'"]\s*:\s*False\s*,\s*[\'"]result[\'"]\s*:\s*.*?(\}\'|\}\")?.*?\}.*'
        
        # Matches the start of the line up to the end of the corrupted part (greedy match for the line)
        # We assume one return statement per line or block.
        # Since dot matches newline with DOTALL, we need be careful.
        # Let's simple use line-based replacement or specific corrupted pattern first.
        
        # Strategy: Replace the messy r"""... replacement block entirely.
        
        # Targeted fix for the specific corruption:
        # r"""...""".replace("{ans}", str(correct_answer))}'.replace('{ans}', str(correct_answer))}
        clean_return_false = 'return {"correct": False, "result": r"""答案錯誤。正確答案為：{ans}""".replace("{ans}", str(correct_answer))}'

        # Replace the corrupted patterns specifically first
        content = content.replace(
            r"""r"""+r"""答案錯誤。正確答案為：{ans}"""+r""".replace("{ans}", str(correct_answer))}'.replace('{ans}', str(correct_answer))}""",
            r"""r"""+r"""答案錯誤。正確答案為：{ans}"""+r""".replace("{ans}", str(correct_answer))}"""
        )
        content = content.replace(
            r"""r"""+r"""答案錯誤。正確答案為：{ans}"""+r""".replace("{ans}", str(correct_answer))}'.replace('{ans}', str(correct_answer))}""",
            r"""r"""+r"""答案錯誤。正確答案為：{ans}"""+r""".replace("{ans}", str(correct_answer))}"""
        )

        # General replacement for the False return statement to standard V10.5
        # This regex looks for: return {... False ... result: ... }
        # And enforces the clean version.
        content = re.sub(
            r'return\s+\{\s*[\'"]correct[\'"]\s*:\s*False\s*,\s*[\'"]result[\'"]\s*:\s*.*\}\'[\s\S]*?\}', # Corrupt ending
            clean_return_false,
            content,
            flags=re.IGNORECASE
        )
        content = re.sub(
             r'return\s+\{\s*[\'"]correct[\'"]\s*:\s*False\s*,\s*[\'"]result[\'"]\s*:\s*.*\}\"[\s\S]*?\}', # Corrupt ending double quote
             clean_return_false,
             content,
             flags=re.IGNORECASE
        )
        
        # Fallback: Just replace the standard good one if it matches the *start* but has junk at the end?
        # Ideally, just strict replace.
        content = re.sub(
            r'return\s+\{\s*[\'"]correct[\'"]\s*:\s*False\s*,\s*[\'"]result[\'"]\s*:\s*r"""答案錯誤.*?replace\("\{ans\}",\s*str\(correct_answer\)\).*?(\}\'|\}\").*?(\}|)',
            clean_return_false,
            content,
            flags=re.DOTALL
        )

        # 4. Patch Management
        # Remove old patches
        patch_pattern = r"(#\s*\[Auto-Injected Patch.*?|def _patch_all_returns\(func\):)[\s\S]*"
        if re.search(patch_pattern, content):
            # Keep content before the patch
            match = re.search(patch_pattern, content)
            content = content[:match.start()].strip()
            
        # Append V10.4 Patch
        content = content + "\n\n" + V10_4_PATCH.strip() + "\n"

        if content != original_content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Fixed: {filename}")
            count += 1
            
    print(f"Total files fixed via V10.5 Protocol: {count}")

if __name__ == "__main__":
    batch_fix_v10_5()
