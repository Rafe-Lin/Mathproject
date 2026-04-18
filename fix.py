import codecs
import re
try:
    with open('models.py', 'r', encoding='utf-16') as f:
        text = f.read()
    with open('models.py', 'w', encoding='utf-8') as f:
        f.write(text)
except Exception:
    pass

try:
    with open('models.py', 'r', encoding='utf-8') as f:
        text = f.read()
    text = re.sub(r'\"docs\"\s*/\s*\"[^\"]+\"\s*/\s*\"skill_breakpoint_catalog\.csv\"', '\"docs\" / \"自適應實作\" / \"skill_breakpoint_catalog.csv\"', text)
    with open('models.py', 'w', encoding='utf-8') as f:
        f.write(text)
except Exception as e:
    print(e)
