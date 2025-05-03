#!/usr/bin/python3
"""
Markdown to HTML converter
"""

import sys
import os
import re
import hashlib

def parse_heading(line):
    """Parse Markdown headings and return HTML"""
    match = re.match(r'^(#+) (.*)', line)
    if match:
        level = len(match.group(1))
        if level > 6:
            level = 6
        return f'<h{level}>{match.group(2)}</h{level}>'
    return None

def parse_unordered_list(line):
    """Parse unordered list items"""
    match = re.match(r'^- (.*)', line)
    if match:
        return f'<li>{parse_text(match.group(1))}</li>'
    return None

def parse_ordered_list(line):
    """Parse ordered list items"""
    match = re.match(r'^\* (.*)', line)
    if match:
        return f'<li>{parse_text(match.group(1))}</li>'
    return None

def parse_text(text):
    """Parse bold and emphasis text"""
    # Handle bold (**text**)
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    # Handle emphasis (__text__)
    text = re.sub(r'__(.*?)__', r'<em>\1</em>', text)
    # Handle [[text]] (MD5)
    text = re.sub(r'\[\[(.*?)\]\]', 
                 lambda m: hashlib.md5(m.group(1).encode()).hexdigest().lower(), 
                 text)
    # Handle ((text)) (remove 'c's case-insensitive)
    text = re.sub(r'\(\((.*?)\)\)', 
                 lambda m: m.group(1).translate(str.maketrans('', '', 'cC')), 
                 text)
    return text

def convert_markdown_to_html(input_file, output_file):
    """Convert Markdown file to HTML"""
    in_list = None
    in_paragraph = False
    html_lines = []
    
    with open(input_file, 'r') as md_file:
        for line in md_file:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                if in_paragraph:
                    html_lines.append('</p>')
                    in_paragraph = False
                if in_list:
                    html_lines.append(f'</{in_list}>')
                    in_list = None
                continue
            
            # Check for headings
            heading = parse_heading(line)
            if heading:
                if in_paragraph:
                    html_lines.append('</p>')
                    in_paragraph = False
                if in_list:
                    html_lines.append(f'</{in_list}>')
                    in_list = None
                html_lines.append(heading)
                continue
            
            # Check for unordered list
            ul_item = parse_unordered_list(line)
            if ul_item:
                if in_paragraph:
                    html_lines.append('</p>')
                    in_paragraph = False
                if in_list != 'ul':
                    if in_list:
                        html_lines.append(f'</{in_list}>')
                    html_lines.append('<ul>')
                    in_list = 'ul'
                html_lines.append(ul_item)
                continue
            
            # Check for ordered list
            ol_item = parse_ordered_list(line)
            if ol_item:
                if in_paragraph:
                    html_lines.append('</p>')
                    in_paragraph = False
                if in_list != 'ol':
                    if in_list:
                        html_lines.append(f'</{in_list}>')
                    html_lines.append('<ol>')
                    in_list = 'ol'
                html_lines.append(ol_item)
                continue
            
            # Handle paragraphs
            if not in_paragraph:
                html_lines.append('<p>')
                in_paragraph = True
            else:
                # Add line break if the line doesn't end a paragraph
                html_lines.append('<br/>')
            
            # Parse the text for bold, emphasis, etc.
            parsed_line = parse_text(line)
            html_lines.append(parsed_line)
    
    # Close any open tags
    if in_paragraph:
        html_lines.append('</p>')
    if in_list:
        html_lines.append(f'</{in_list}>')
    
    # Write to output file
    with open(output_file, 'w') as html_file:
        html_file.write('\n'.join(html_lines))

def main():
    if len(sys.argv) < 3:
        print("Usage: ./markdown2html.py README.md README.html", file=sys.stderr)
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if not os.path.exists(input_file):
        print(f"Missing {input_file}", file=sys.stderr)
        sys.exit(1)
    
    convert_markdown_to_html(input_file, output_file)
    sys.exit(0)

if __name__ == "__main__":
    main()
