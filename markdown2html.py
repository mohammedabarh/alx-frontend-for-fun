#!/usr/bin/python3
"""
Markdown to HTML Converter
"""
import sys
import os
import re
import hashlib

def convert_markdown_to_html(input_file, output_file):
    """Converts markdown file to HTML file"""
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Missing {input_file}", file=sys.stderr)
        sys.exit(1)

    # Read markdown content
    with open(input_file, 'r') as f:
        content = f.read()

    # Convert headings
    for i in range(6, 0, -1):
        pattern = f"^{'#' * i} (.+)$"
        content = re.sub(pattern, f"<h{i}>\\1</h{i}>", content, flags=re.MULTILINE)

    # Convert unordered lists
    content = convert_lists(content, "-", "ul")
    
    # Convert ordered lists
    content = convert_lists(content, "*", "ol")

    # Convert paragraphs and line breaks
    content = convert_paragraphs(content)

    # Convert bold and emphasis text
    content = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', content)
    content = re.sub(r'__(.+?)__', r'<em>\1</em>', content)

    # Convert MD5 brackets
    content = convert_md5_brackets(content)

    # Convert special parentheses
    content = convert_special_parentheses(content)

    # Write to output file
    with open(output_file, 'w') as f:
        f.write(content)

def convert_lists(content, marker, list_type):
    """Converts markdown lists to HTML lists"""
    lines = content.split('\n')
    in_list = False
    result = []
    
    for line in lines:
        if line.startswith(f"{marker} "):
            if not in_list:
                result.append(f"<{list_type}>")
                in_list = True
            item = line[2:]
            result.append(f"<li>{item}</li>")
        else:
            if in_list:
                result.append(f"</{list_type}>")
                in_list = False
            result.append(line)
    
    if in_list:
        result.append(f"</{list_type}>")
    
    return '\n'.join(result)

def convert_paragraphs(content):
    """Converts markdown paragraphs to HTML paragraphs"""
    paragraphs = content.split('\n\n')
    result = []
    
    for p in paragraphs:
        if p.strip() and not p.startswith(('<h', '<ul', '<ol')):
            lines = p.split('\n')
            if len(lines) > 1:
                p = '<br/>\n'.join(lines)
            result.append(f"<p>\n{p}\n</p>")
        else:
            result.append(p)
    
    return '\n'.join(result)

def convert_md5_brackets(content):
    """Converts [[text]] to MD5 hash"""
    def md5_replace(match):
        text = match.group(1)
        return hashlib.md5(text.encode()).hexdigest()
    
    return re.sub(r'\[\[(.+?)\]\]', md5_replace, content)

def convert_special_parentheses(content):
    """Converts ((text)) by removing all 'c' characters"""
    def remove_c(match):
        text = match.group(1)
        return text.replace('c', '').replace('C', '')
    
    return re.sub(r'\(\((.+?)\)\)', remove_c, content)

if __name__ == "__main__":
    # Check arguments
    if len(sys.argv) < 3:
        print("Usage: ./markdown2html.py README.md README.html", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    convert_markdown_to_html(input_file, output_file)
    sys.exit(0)
