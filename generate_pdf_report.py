#!/usr/bin/env python3
"""
Script to generate a PDF report from the Markdown report file.
This script converts the project_report.md file to a professionally formatted PDF.
"""

import markdown
import os
import sys
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

def generate_pdf_report():
    """
    Convert the Markdown report to PDF format with professional styling.
    """
    
    # File paths
    markdown_file = "project_report.md"
    html_file = "project_report.html"
    pdf_file = "BYN_Project_Report.pdf"
    
    if not os.path.exists(markdown_file):
        print(f"Error: {markdown_file} not found!")
        print("Please make sure the Markdown report file exists.")
        return False
    
    # Read the Markdown content
    with open(markdown_file, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # Convert Markdown to HTML
    md = markdown.Markdown(extensions=[
        'markdown.extensions.tables',
        'markdown.extensions.toc',
        'markdown.extensions.codehilite',
        'markdown.extensions.fenced_code'
    ])
    
    html_content = md.convert(markdown_content)
    
    # Add CSS styling for professional appearance
    css_styles = """
    <style>
    @page {
        size: A4;
        margin: 2cm;
        @bottom-center {
            content: counter(page);
        }
    }
    
    body {
        font-family: 'Arial', sans-serif;
        line-height: 1.6;
        color: #333;
        max-width: 100%;
    }
    
    h1 {
        color: #2c3e50;
        border-bottom: 3px solid #3498db;
        padding-bottom: 10px;
        page-break-before: always;
    }
    
    h1:first-child {
        page-break-before: avoid;
    }
    
    h2 {
        color: #34495e;
        border-bottom: 2px solid #ecf0f1;
        padding-bottom: 5px;
        margin-top: 30px;
    }
    
    h3 {
        color: #2c3e50;
        margin-top: 25px;
    }
    
    h4 {
        color: #34495e;
        margin-top: 20px;
    }
    
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    th, td {
        border: 1px solid #ddd;
        padding: 12px;
        text-align: left;
    }
    
    th {
        background-color: #3498db;
        color: white;
        font-weight: bold;
    }
    
    tr:nth-child(even) {
        background-color: #f8f9fa;
    }
    
    code {
        background-color: #f8f9fa;
        padding: 2px 6px;
        border-radius: 3px;
        font-family: 'Courier New', monospace;
        font-size: 0.9em;
    }
    
    pre {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 5px;
        border-left: 4px solid #3498db;
        overflow-x: auto;
    }
    
    ul, ol {
        margin: 15px 0;
        padding-left: 30px;
    }
    
    li {
        margin: 8px 0;
    }
    
    blockquote {
        border-left: 4px solid #3498db;
        padding-left: 20px;
        margin: 20px 0;
        font-style: italic;
        background-color: #f8f9fa;
        padding: 15px;
    }
    
    .cover-page {
        text-align: center;
        page-break-after: always;
        margin-top: 100px;
    }
    
    .cover-page h1 {
        font-size: 2.5em;
        margin-bottom: 30px;
        border: none;
    }
    
    .cover-page h3 {
        font-size: 1.2em;
        margin: 10px 0;
        color: #7f8c8d;
    }
    
    hr {
        border: none;
        border-top: 2px solid #ecf0f1;
        margin: 30px 0;
    }
    
    .page-break {
        page-break-before: always;
    }
    
    strong {
        color: #2c3e50;
    }
    
    .toc {
        page-break-after: always;
    }
    
    .fig-caption {
        text-align: center;
        font-style: italic;
        margin: 10px 0;
        color: #7f8c8d;
    }
    
    @media print {
        h1, h2, h3, h4, h5, h6 {
            page-break-after: avoid;
        }
        
        table, figure, img {
            page-break-inside: avoid;
        }
    }
    </style>
    """
    
    # Create complete HTML document
    html_document = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>BYN Project Report</title>
        {css_styles}
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    # Save HTML file
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_document)
    
    try:
        # Convert HTML to PDF
        print("Converting to PDF...")
        font_config = FontConfiguration()
        
        html_doc = HTML(string=html_document, base_url=".")
        css_doc = CSS(string="""
            @page {
                size: A4;
                margin: 2cm;
                @bottom-center {
                    content: "Page " counter(page) " of " counter(pages);
                    font-size: 10px;
                    color: #666;
                }
            }
        """, font_config=font_config)
        
        html_doc.write_pdf(pdf_file, stylesheets=[css_doc], font_config=font_config)
        
        # Clean up HTML file
        if os.path.exists(html_file):
            os.remove(html_file)
        
        print(f"✅ PDF report generated successfully: {pdf_file}")
        print(f"📄 File size: {os.path.getsize(pdf_file) / 1024:.1f} KB")
        return True
        
    except Exception as e:
        print(f"❌ Error generating PDF: {str(e)}")
        print("\nTo install required dependencies, run:")
        print("pip install markdown weasyprint")
        return False

def install_dependencies():
    """
    Install required dependencies for PDF generation.
    """
    print("Installing required dependencies...")
    os.system("pip install markdown weasyprint")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--install-deps":
        install_dependencies()
    else:
        success = generate_pdf_report()
        if not success:
            print("\nIf you encounter dependency issues, run:")
            print("python generate_pdf_report.py --install-deps") 