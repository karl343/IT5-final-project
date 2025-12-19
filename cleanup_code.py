import re
import os
import ast

def remove_comments_and_docstrings(source):
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
            if ast.get_docstring(node):
                node.body = node.body[1:] if node.body else []
    
    lines = source.split('\n')
    cleaned_lines = []
    in_multiline_string = False
    multiline_char = None
    
    for line in lines:
        stripped = line.strip()
        
        if not in_multiline_string:
            if stripped.startswith('"""') or stripped.startswith("'''"):
                multiline_char = stripped[:3]
                if stripped.count(multiline_char) == 2 and len(stripped) > 3:
                    continue
                in_multiline_string = True
                continue
            elif stripped.startswith('#'):
                continue
            
            cleaned_line = line
            if '#' in line:
                parts = line.split('#')
                if parts[0].strip():
                    cleaned_line = parts[0].rstrip()
                else:
                    continue
            cleaned_lines.append(cleaned_line)
        else:
            if multiline_char in line:
                in_multiline_string = False
                multiline_char = None
            continue
    
    result = '\n'.join(cleaned_lines)
    result = re.sub(r'\n{3,}', '\n\n', result)
    return result

def clean_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        cleaned = remove_comments_and_docstrings(content)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(cleaned)
        
        print(f"Cleaned: {filepath}")
    except Exception as e:
        print(f"Error cleaning {filepath}: {e}")

if __name__ == "__main__":
    swiftpay_dir = "SwiftPay"
    for root, dirs, files in os.walk(swiftpay_dir):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                clean_file(filepath)

