#!/usr/bin/python3
"""
Markdown to HTML converter
Converts Markdown files to HTML with support for:
- Headings (#, ##, etc.)
- Lists (unordered -, ordered *)
- Paragraphs and line breaks
- Text formatting (**bold**, __emphasis__)
- Special syntax ([[MD5]], ((remove 'c's))
"""

import sys
import os
import re
import hashlib

def parse_heading(line):
    """Parse Markdown headings into HTML headings"""
    match = re.match(r'^(#+) (.*)', line)
    if match:
        level = min(len(match.group(1)), 6)  # Max h6
        return f'<h{level}>{match.group(2)}</h{level}>'
    return None

def parse_list_item(line, list_type):
    """Parse list items (both unordered and ordered)"""
    if list_type == 'ul':
        match = re.match(r'^- (.*)', line)
    else:  # ol
        match = re.match(r'^\* (.*)', line)
    if match:
        return f'<li>{parse_inline_formatting(match.group(1))}</li>'
    return None

def parse_inline_formatting(text):
    """Handle inline formatting and special syntax"""
    # Bold: **text** → <b>text</b>
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    # Emphasis: __text__ → <em>text</em>
    text = re.sub(r'__(.*?)__', r'<em>\1</em>', text)
    # MD5: [[text]] → md5 hash
    text = re.sub(r'\[\[(.*?)\]\]', 
                 lambda m: hashlib.md5(m.group(1).encode()).hexdigest().lower(), 
                 text)
    # Remove 'c's: ((text)) → text with 'c's removed
    text = re.sub(r'\(\((.*?)\)\)', 
                 lambda m: m.group(1).translate(str.maketrans('', '', 'cC')), 
                 text)
    return text

def convert_markdown_to_html(input_file, output_file):
    """Main conversion function"""
    html_lines = []
    current_list = None
    in_paragraph = False

    with open(input_file, 'r') as md_file:
        for line in md_file:
            line = line.rstrip()  # Remove trailing whitespace

            # Handle empty lines (end current blocks)
            if not line:
                if in_paragraph:
                    html_lines.append('</p>')
                    in_paragraph = False
                if current_list:
                    html_lines.append(f'</{current_list}>')
                    current_list = None
                continue

            # Try parsing as heading first
            heading = parse_heading(line)
            if heading:
                close_blocks(html_lines, current_list, in_paragraph)
                html_lines.append(heading)
                current_list, in_paragraph = None, False
                continue

            # Try parsing as unordered list
            ul_item = parse_list_item(line, 'ul')
            if ul_item:
                handle_list_item(html_lines, ul_item, 'ul', current_list, in_paragraph)
                current_list, in_paragraph = 'ul', False
                continue

            # Try parsing as ordered list
            ol_item = parse_list_item(line, 'ol')
            if ol_item:
                handle_list_item(html_lines, ol_item, 'ol', current_list, in_paragraph)
                current_list, in_paragraph = 'ol', False
                continue

            # Handle as paragraph text
            if not in_paragraph:
                html_lines.append('<p>')
                in_paragraph = True
            else:
                html_lines.append('<br/>')
            
            formatted_line = parse_inline_formatting(line)
            html_lines.append(formatted_line)

    # Close any remaining open tags
    close_blocks(html_lines, current_list, in_paragraph)

    # Write to output file
    with open(output_file, 'w') as html_file:
        html_file.write('\n'.join(html_lines))

def close_blocks(html_lines, current_list, in_paragraph):
    """Close any open HTML blocks"""
    if in_paragraph:
        html_lines.append('</p>')
    if current_list:
        html_lines.append(f'</{current_list}>')

def handle_list_item(html_lines, item, list_type, current_list, in_paragraph):
    """Handle list item parsing and proper nesting"""
    if in_paragraph:
        html_lines.append('</p>')
    if current_list != list_type:
        if current_list:
            html_lines.append(f'</{current_list}>')
        html_lines.append(f'<{list_type}>')
    html_lines.append(item)

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
