from fpdf import FPDF

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Frontend Section of Project Report', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def add_cover_page(self):
        self.add_page()
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'University Name', 0, 1, 'C')
        self.cell(0, 10, 'Lecture Name', 0, 1, 'C')
        self.cell(0, 10, 'Semester', 0, 1, 'C')
        self.cell(0, 10, 'Project Name', 0, 1, 'C')
        self.cell(0, 10, 'Team Members', 0, 1, 'C')

    def add_introduction(self):
        self.add_page()
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, 'Introduction:\nThis section defines the problem and objectives of the project.')

    def add_technologies_used(self):
        self.add_page()
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, 'Technologies Used:\n- React.js\n- TypeScript\n- Tailwind CSS\n- Vercel\n- Axios')

    def add_software_architecture(self):
        self.add_page()
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, 'Software Architecture:\nFrontend: Component-based architecture with key components like Navbar, PostCard, CommentsSection, and LoadingSpinner.\nBackend Integration: API calls using Axios.\nDatabase: Interaction with backend APIs.')

    def add_screenshots(self):
        self.add_page()
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, 'Screenshots:\nInclude screenshots of the main pages with explanations.')

    def add_conclusion(self):
        self.add_page()
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, 'Conclusion:\nSummarize the frontend\'s role in the project and its contribution to the overall functionality.')

    def add_references(self):
        self.add_page()
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, 'References:\n- React.js Documentation\n- TypeScript Documentation\n- Tailwind CSS Documentation\n- Axios Documentation\n- Vercel Documentation')

if __name__ == '__main__':
    pdf = PDFReport()
    pdf.add_cover_page()
    pdf.add_introduction()
    pdf.add_technologies_used()
    pdf.add_software_architecture()
    pdf.add_screenshots()
    pdf.add_conclusion()
    pdf.add_references()
    pdf.output('frontend_project_report.pdf')
