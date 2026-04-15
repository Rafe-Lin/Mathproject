import os
import re

SKILLS_DIR = r"d:\Python\Mathproject\skills"

# V10.4 Universal Patch Code (Minified for Injection)
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

def batch_upgrade_v10_4():
    count = 0
    for filename in os.listdir(SKILLS_DIR):
        if not filename.endswith(".py") or filename == "__init__.py":
            continue
            
        filepath = os.path.join(SKILLS_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        original_content = content
        
        # 1. Matplotlib Font Fix (Double Quotes)
        # Replaces any variation of font setting with the strict version
        content = re.sub(
            r"matplotlib\.rcParams\s*\[\s*['\"]font\.sans-serif['\"]\s*\]\s*=\s*\[.*?\]",
            'matplotlib.rcParams["font.sans-serif"] = ["Microsoft JhengHei"]',
            content,
            flags=re.IGNORECASE
        )

        # 2. Update 'Correct' return (Strict JSON Double Quotes)
        # Matches previous V10.3 versions or older variants
        content = re.sub(
            r"return\s+\{\s*['\"]correct['\"]\s*:\s*True\s*,\s*['\"]result['\"]\s*:\s*['\"].*?['\"]\s*\}",
            'return {"correct": True, "result": "正確！"}',
            content,
            flags=re.IGNORECASE
        )

        # 3. Update 'Incorrect' return (Triple Quotes Protection)
        # Matches previous V10.3 versions or older variants
        content = re.sub(
            r"return\s+\{\s*['\"]correct['\"]\s*:\s*False\s*,\s*['\"]result['\"]\s*:\s*.*?\s*\}",
            'return {"correct": False, "result": r"""答案錯誤。正確答案為：{ans}""".replace("{ans}", str(correct_answer))}',
            content,
            flags=re.IGNORECASE | re.DOTALL
        )

        # 4. Remove Old Patches & Inject V10.4 Patch
        # Find start of existing patch
        patch_pattern = r"(#\s*\[Auto-Injected Patch.*?|def _patch_all_returns\(func\):)"
        match = re.search(patch_pattern, content, re.DOTALL)
        
        if match:
            # Truncate content before the patch
            content = content[:match.start()].strip() + "\n\n" + V10_4_PATCH.strip() + "\n"
        else:
            # Append if no patch found (unlikely for existing files, but safe)
            content = content.strip() + "\n\n" + V10_4_PATCH.strip() + "\n"

        if content != original_content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Upgraded: {filename}")
            count += 1
            
    print(f"Total files upgraded to V10.4: {count}")

if __name__ == "__main__":
    batch_upgrade_v10_4()
