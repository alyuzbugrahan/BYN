# BYN Project Report Generation Guide

This guide explains how to generate a professional PDF report from the Markdown report file.

## 📋 Prerequisites

- Python 3.6 or higher
- Internet connection (for installing dependencies)

## 🚀 Quick Start

### Option 1: Automatic Installation and Generation

```bash
# Install dependencies and generate PDF in one command
python generate_pdf_report.py --install-deps
python generate_pdf_report.py
```

### Option 2: Manual Installation

```bash
# Install required Python packages
pip install markdown weasyprint

# Generate the PDF report
python generate_pdf_report.py
```

## 📁 Generated Files

After running the script, you'll find:

- `BYN_Project_Report.pdf` - The final PDF report
- The original `project_report.md` remains unchanged

## 📖 Report Structure

The generated PDF report includes:

1. **Cover Page** - University information, course details, team members
2. **Table of Contents** - Navigational structure
3. **Introduction** - Problem definition and objectives
4. **Technologies Used** - Complete technology stack
5. **Software Architecture** - System design and API structure
6. **Database Design** - Entity relationships and schema
7. **Screenshots and Features** - Visual demonstrations
8. **Conclusion** - Achievements and future work
9. **References** - Academic and technical citations

## 🎨 Report Features

- **Professional Formatting**: Clean, academic-style layout
- **Tables and Figures**: Properly numbered and captioned
- **Code Highlighting**: Syntax highlighting for code blocks
- **Cross-References**: Internal links and citations
- **Page Numbers**: Automatic page numbering
- **Print-Ready**: Optimized for A4 paper size

## 🔧 Customization

### Modifying University Information

Edit the cover page section in `project_report.md`:

```markdown
**University:** [Your University Name]  
**Course:** [Your Course Name]  
**Semester:** [Current Semester/Year]  
**Team Members:** [Your Team Member Names]
```

### Adding Screenshots

To add actual screenshots:

1. Take screenshots of your application
2. Save them in a `screenshots/` folder
3. Update the report with actual image references:

```markdown
![Login Interface](screenshots/login.png)
*Fig.3: User Authentication Interface*
```

### Customizing Styling

Modify the CSS styles in `generate_pdf_report.py` to change:
- Colors and fonts
- Table styling
- Page layout
- Header/footer formatting

## 🛠️ Troubleshooting

### Common Issues

**1. WeasyPrint Installation Issues**

On Windows:
```bash
# Install Microsoft Visual C++ Build Tools first
# Then install weasyprint
pip install weasyprint
```

On macOS:
```bash
# Install using Homebrew first
brew install python-tk
pip install weasyprint
```

On Linux:
```bash
# Install system dependencies
sudo apt-get install python3-dev python3-pip python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
pip install weasyprint
```

**2. Font Issues**

If you encounter font-related errors:
```bash
# Install additional font packages
pip install fonttools
```

**3. Large File Size**

If the PDF is too large:
- Optimize images before adding them
- Reduce image resolution
- Use JPEG instead of PNG for photos

### Alternative PDF Generation

If WeasyPrint doesn't work, you can use alternative methods:

**Method 1: Using Pandoc**
```bash
# Install pandoc
# On Windows: Download from https://pandoc.org/installing.html
# On macOS: brew install pandoc
# On Linux: sudo apt-get install pandoc

# Convert to PDF
pandoc project_report.md -o BYN_Project_Report.pdf --pdf-engine=xelatex
```

**Method 2: Using Markdown to HTML to PDF**
1. Convert MD to HTML using any markdown processor
2. Open HTML in browser
3. Print to PDF with browser's print function

## 📊 Quality Checklist

Before submitting your report, ensure:

- [ ] All university information is filled in
- [ ] Team member names are listed
- [ ] All figures are properly numbered (Fig.1, Fig.2, etc.)
- [ ] All tables are properly numbered (Table 1, Table 2, etc.)
- [ ] Citations are included in paragraphs
- [ ] References section is complete
- [ ] Screenshots are clear and relevant
- [ ] Code formatting is consistent
- [ ] Page breaks are appropriate
- [ ] No orphaned headings

## 📤 Submission

The generated `BYN_Project_Report.pdf` is ready for submission. The report follows academic standards with:

- Professional formatting
- Proper citations and references
- Numbered figures and tables
- Clean layout and typography
- Comprehensive technical content

## 🆘 Support

If you encounter issues:

1. Check that all dependencies are installed correctly
2. Ensure Python version is 3.6+
3. Try the alternative PDF generation methods
4. Check the troubleshooting section above

For technical issues with the BYN project itself, refer to the main `README.md` file.

---

*This guide ensures you can generate a professional, submission-ready PDF report for your BYN project.* 