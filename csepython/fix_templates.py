import os
import re

templates_dir = "home/templates"

for filename in os.listdir(templates_dir):
    if not filename.endswith(".html"):
        continue
    
    filepath = os.path.join(templates_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if this is a base.html - skip it
    if filename == "base.html":
        continue
    
    # Remove duplicate {% extends "base.html" %} lines
    content = re.sub(r'(\{% extends "base\.html" %\})', r'\1', content, count=1)
    content = content.replace('{% extends "base.html" %}', '', 1)
    content = '{% extends "base.html" %}\n' + content
    
    # Remove duplicate {% block content %} lines
    content = re.sub(r'(\{% block content %\})', r'\1', content, count=1)
    
    # Remove duplicate {% load static %} lines (keep only first)
    static_lines = re.findall(r'\{% load static %\}', content)
    if len(static_lines) > 1:
        content = re.sub(r'\{% load static %\}', '', content, count=len(static_lines)-1)
    
    # Add {% load static %} right after extends if not present
    if '{% load static %}' not in content:
        content = content.replace('{% extends "base.html" %}', '{% extends "base.html" %}\n{% load static %}')
    
    # Remove duplicate DOCTYPE and html tags (they come from base.html)
    content = re.sub(r'<!DOCTYPE html>', '', content)
    content = re.sub(r'<html[^>]*>', '', content)
    content = re.sub(r'</html>', '', content)
    content = re.sub(r'<head[^>]*>', '', content)
    content = re.sub(r'</head>', '', content)
    content = re.sub(r'<body[^>]*>', '', content)
    content = re.sub(r'</body>', '', content)
    
    # Clean up extra blank lines
    content = re.sub(r'\n\s*\n', '\n\n', content)
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Fixed: {filename}")

print("🎉 All templates fixed!")
