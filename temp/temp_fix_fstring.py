# -*- coding: utf-8 -*-

# Read the file
with open(r'd:\Python\Mathproject\core\code_generator.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace f""" with """ and change variable interpolation from {var} to {var}
# The key is to change from f-string to .format() method

# Find the prompt definition (starts at line 76)
old_start = '    # 3. 構建 Prompt\n    prompt = f"""'
new_start = '    # 3. 構建 Prompt\n    prompt = """'

if old_start in content:
    content = content.replace(old_start, new_start)
    print("[OK] Changed f-string to regular string")
else:
    print("[FAIL] Could not find f-string start")

# Now we need to add .format() at the end of the prompt
# Find the end of the prompt (line 167: """)
# We need to find the specific location where the prompt ends

# The prompt ends with: Now, generate the Python code for '{skill_id}'.\n    """
# We need to change this to use .format() instead

old_end = "    Now, generate the Python code for '{skill_id}'.\n    \"\"\""
new_end = "    Now, generate the Python code for '{{skill_id}}'.\n    \"\"\".format(\n        skill_id=skill_id,\n        topic_description=topic_description,\n        input_type=input_type,\n        examples_text=examples_text,\n        template_code=template_code\n    )"

if old_end in content:
    content = content.replace(old_end, new_end)
    print("[OK] Added .format() method with variables")
else:
    print("[FAIL] Could not find prompt end")
    # Try alternative
    alt_end = "    Now, generate the Python code for '{skill_id}'.\r\n    \"\"\""
    if alt_end in content:
        new_end_alt = "    Now, generate the Python code for '{{skill_id}}'.\r\n    \"\"\".format(\r\n        skill_id=skill_id,\r\n        topic_description=topic_description,\r\n        input_type=input_type,\r\n        examples_text=examples_text,\r\n        template_code=template_code\r\n    )"
        content = content.replace(alt_end, new_end_alt)
        print("[OK] Added .format() method with variables (CRLF version)")

# Now replace all {variable} with {{variable}} in the prompt content
# But we need to be careful - only in the prompt section

# Replace the variable placeholders to use double braces for .format()
replacements = [
    ('Target Skill ID: {skill_id}', 'Target Skill ID: {{skill_id}}'),
    ('Topic Description: {topic_description}', 'Topic Description: {{topic_description}}'),
    ('Input Type: {input_type}', 'Input Type: {{input_type}}'),
    ('{examples_text}', '{{examples_text}}'),
    ('{template_code}', '{{template_code}}'),
    ('`static/generated_plots/{skill_id}_', '`static/generated_plots/{{skill_id}}_'),
]

for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        print(f"[OK] Replaced {old[:30]}...")

# Write back to file
with open(r'd:\Python\Mathproject\core\code_generator.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n[SUCCESS] Converted f-string to .format() method!")
print("The prompt now uses regular string with .format() for variable interpolation.")
