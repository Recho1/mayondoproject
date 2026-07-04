import os
import re

templates_dir = "home/templates"

# Get all HTML files
for filename in os.listdir(templates_dir):
    if not filename.endswith(".html"):
        continue
    
    filepath = os.path.join(templates_dir, filename)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Skip base.html
    if filename == "base.html":
        continue
    
    # Check if the file has the duplicate block issue
    if '{% block content %}' in content:
        # Count occurrences
        block_count = content.count('{% block content %}')
        extends_count = content.count('{% extends "base.html" %}')
        
        if block_count > 1 or extends_count > 1:
            print(f"Fixing: {filename} (block: {block_count}, extends: {extends_count})")
            
            # Keep only the first block content and remove the rest
            lines = content.split('\n')
            new_lines = []
            found_block = False
            found_extends = False
            
            for line in lines:
                # Skip duplicate extends
                if '{% extends "base.html" %}' in line:
                    if not found_extends:
                        new_lines.append('{% extends "base.html" %}')
                        found_extends = True
                    continue
                
                # Skip duplicate block content
                if '{% block content %}' in line:
                    if not found_block:
                        new_lines.append('{% block content %}')
                        found_block = True
                    continue
                
                # Skip duplicate endblock
                if '{% endblock %}' in line:
                    if found_block:
                        new_lines.append('{% endblock %}')
                        found_block = False
                    continue
                
                new_lines.append(line)
            
            # Make sure we have extends at the top
            final_content = '\n'.join(new_lines)
            if '{% extends "base.html" %}' not in final_content:
                final_content = '{% extends "base.html" %}\n' + final_content
            
            # Make sure we have load static
            if '{% load static %}' not in final_content:
                final_content = final_content.replace('{% extends "base.html" %}', '{% extends "base.html" %}\n{% load static %}')
            
            # Remove any HTML structure that belongs in base.html
            final_content = re.sub(r'<!DOCTYPE html>', '', final_content)
            final_content = re.sub(r'<html[^>]*>', '', final_content)
            final_content = re.sub(r'</html>', '', final_content)
            final_content = re.sub(r'<head[^>]*>', '', final_content)
            final_content = re.sub(r'</head>', '', final_content)
            final_content = re.sub(r'<body[^>]*>', '', final_content)
            final_content = re.sub(r'</body>', '', final_content)
            
            # Write back
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(final_content)
            
            print(f"✅ Fixed: {filename}")

print("🎉 All templates fixed!")
