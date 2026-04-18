# -*- coding: utf-8 -*-

# Read the file
with open(r'd:\Python\Mathproject\core\code_generator.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the prompt section
start_marker = 'prompt = """'
end_marker = '""".format('

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx != -1 and end_idx != -1:
    # Extract prompt content
    prompt_full = content[start_idx:end_idx]
    
    # We want to replace {{ with {{{{ and }} with }}}}
    # But we must be careful not to touch anything outside the prompt
    # And we must be careful about the order (don't replace {{{{ with {{{{{{{{)
    
    # Actually, simply replacing {{ with {{{{ is safe if we do it once
    # variables are {var}, so they are not affected.
    
    new_prompt_full = prompt_full.replace('{{', '{{{{').replace('}}', '}}}}')
    
    # Replace in content
    content = content.replace(prompt_full, new_prompt_full)
    print("[OK] Doubled all double braces in prompt")

# Write back to file
with open(r'd:\Python\Mathproject\core\code_generator.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n[SUCCESS] Fixed prompt brace escaping!")
