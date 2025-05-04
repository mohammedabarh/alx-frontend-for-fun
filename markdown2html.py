#!/usr/bin/python3
"""
Markdown to HTML Converter
"""
import sys
import os
import re
import hashlib


def convert_md5(text):
    """Convert text to MD5 hash"""
    return hashlib.md5(text.encode()).hexdigest()


def remove_c(text):
    """Remove all 'c' characters (case insensitive) from text"""
    return re.sub(r'[cC]', '', text)


def parse_headings(line):
    """Parse markdown headings"""
    heading_match = re.match(r'^(#{1,6})\s(.+)$', line)
    if heading_match:
        level = len(heading_match.group(1))
        content = heading_match.group(2)
        return f"<h{level}>{content}</h{level}>"
    return line


def parse_lists(lines):
    """Parse unordered and ordered lists"""
    html_lines = []
    in_list = False
    list_type = None
    
    for line in lines:
        if line.startswith('- '):
            if not in_list or list_type != 'ul':
                if in_list:
                    html_lines.append(f"</{list_type}>")
                html_lines.append("<ul>")
                in_list = True
                list_type = 'ul'
            html_lines.append(f"<li>{line[2:]}</li>")
        
        elif line.startswith('* '):
            if not in_list or list_type != 'ol':
                if in_list:
                    html_lines.append(f"</{list_type}>")
                html_lines.append("<ol>")
                in_list = True
                list_type = 'ol'
            html_lines.append(f"<li>{line[2:]}</li>")
        
        else:
            if in_list:
                html_lines.append(f"</{list_type}>")
                in_list = False
            html_lines.append(line)
    
    if in_list:
        html_lines.append(f"</{list_type}>")
    
    return html_lines


def parse_emphasis(line):
    """Parse bold and emphasis text"""
    # Handle bold text
    line = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', line)
    # Handle emphasis text
    line = re.sub(r'__(.+?)__', r'<em>\1</em>', line)
    return line


def parse_special_syntax(line):
    """Parse MD5 and remove C syntax"""
    # Handle MD5 conversion
    md5_matches = re.findall(r'\[\[(.+?)\]\]', line)
    for match in md5_matches:
        line = line.replace(f"[[{match}]]", convert_md5(match))
    
    # Handle remove C
    c_matches = re.findall(r'\(\((.+?)\)\)', line)
    for match in c_matches:
        line = line.replace(f"(({match}))", remove_c(match))
    
    return line


def parse_paragraphs(lines):
    """Parse paragraphs and line breaks"""
    html_lines = []
    current_paragraph = []
    
    for line in lines:
        if line.strip() == '':
            if current_paragraph:
                paragraph_content = '<br/>'.join(current_paragraph)
                html_lines.append(f"<p>\n{paragraph_content}\n</p>")
                current_paragraph = []
        else:
            current_paragraph.append(line)
    
    if current_paragraph:
        paragraph_content = '<br/>'.join(current_paragraph)
        html_lines.append(f"<p>\n{paragraph_content}\n</p>")
    
    return html_lines


def markdown_to_html(input_file, output_file):
    """Convert markdown file to HTML"""
    try:
        with open(input_file, 'r') as f:
            content = f.read().splitlines()
    except FileNotFoundError:
        print(f"Missing {input_file}", file=sys.stderr)
        sys.exit(1)

    # Process the content
    html_lines = []
    for line in content:
        # Parse headings
        line = parse_headings(line)
        # Parse emphasis
        line = parse_emphasis(line)
        # Parse special syntax
        line = parse_special_syntax(line)
        html_lines.append(line)

    # Parse lists
    html_lines = parse_lists(html_lines)
    
    # Parse paragraphs
    html_lines = parse_paragraphs(html_lines)

    # Write to output file
    with open(output_file, 'w') as f:
        f.write('\n'.join(html_lines))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: ./markdown2html.py README.md README.html", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    markdown_to_html(input_file, output_file)
    sys.exit(0)
