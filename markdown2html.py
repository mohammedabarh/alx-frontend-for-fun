#!/usr/bin/python3
"""
Markdown to HTML Converter
"""
import sys
import os
import re
import hashlib


def convert_headings(line):
    """Convert markdown headings to HTML"""
    pattern = r'^(#{1,6})\s(.+)$'
    match = re.match(pattern, line)
    if match:
        level = len(match.group(1))
        return f'<h{level}>{match.group(2)}</h{level}>\n'
    return line


def convert_md5(text):
    """Convert text in [[]] to MD5 hash"""
    pattern = r'\[\[(.+?)\]\]'
    
    def md5_replace(match):
        content = match.group(1)
        return hashlib.md5(content.encode()).hexdigest()
    
    return re.sub(pattern, md5_replace, text)


def remove_c(text):
    """Remove all 'c' characters from text in (())"""
    pattern = r'\(\((.+?)\)\)'
    
    def c_remove(match):
        content = match.group(1)
        return ''.join(c for c in content if c.lower() != 'c')
    
    return re.sub(pattern, c_remove, text)


def convert_emphasis(text):
    """Convert markdown emphasis to HTML"""
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'__(.+?)__', r'<em>\1</em>', text)
    return text


def process_markdown(input_file, output_file):
    """Process markdown file and convert to HTML"""
    try:
        with open(input_file, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Missing {input_file}", file=sys.stderr)
        sys.exit(1)

    html_lines = []
    current_list = []
    list_type = None
    in_paragraph = False

    for line in lines:
        line = line.rstrip()
        
        # Process special syntax first
        line = convert_md5(line)
        line = remove_c(line)
        line = convert_emphasis(line)

        # Handle headings
        if line.startswith('#'):
            if in_paragraph:
                html_lines.append('</p>')
                in_paragraph = False
            if current_list:
                html_lines.append(f'</{list_type}>')
                current_list = []
            html_lines.append(convert_headings(line))
            continue

        # Handle lists
        if line.startswith('- ') or line.startswith('* '):
            if in_paragraph:
                html_lines.append('</p>')
                in_paragraph = False

            new_list_type = 'ul' if line.startswith('- ') else 'ol'
            list_item = line[2:].strip()

            if not current_list:
                list_type = new_list_type
                html_lines.append(f'<{list_type}>')
            elif list_type != new_list_type:
                html_lines.append(f'</{list_type}>')
                list_type = new_list_type
                html_lines.append(f'<{list_type}>')

            html_lines.append(f'<li>{list_item}</li>')
            current_list.append(list_item)
            continue

        # Close list if line is not a list item
        if current_list and not (line.startswith('- ') or line.startswith('* ')):
            html_lines.append(f'</{list_type}>')
            current_list = []
            list_type = None

        # Handle paragraphs
        if line.strip():
            if not in_paragraph:
                html_lines.append('<p>')
                in_paragraph = True
            else:
                html_lines.append('<br/>')
            html_lines.append(line)
        elif in_paragraph:
            html_lines.append('</p>')
            in_paragraph = False

    # Close any open tags
    if current_list:
        html_lines.append(f'</{list_type}>')
    if in_paragraph:
        html_lines.append('</p>')

    # Write to output file
    try:
        with open(output_file, 'w') as f:
            f.write('\n'.join(html_lines))
    except Exception as e:
        print(f"Error writing to {output_file}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: ./markdown2html.py README.md README.html", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    process_markdown(input_file, output_file)
    sys.exit(0)
