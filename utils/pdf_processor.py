import PyPDF2
from io import BytesIO
import re

class PDFProcessor:
    @staticmethod
    def extract_text(pdf_file):
        """Extract text content from uploaded PDF file."""
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_file))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text.strip()
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")

    @staticmethod
    def clean_text(text):
        """Clean and normalize extracted text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters
        text = re.sub(r'[^\w\s\-.,;:]', '', text)
        return text.strip()

    @staticmethod
    def extract_sections(text):
        """Extract common syllabus sections."""
        sections = {
            'course_objectives': '',
            'learning_outcomes': '',
            'course_content': '',
            'assessment': '',
            'prerequisites': ''
        }
        
        # Simple pattern matching for common syllabus sections
        patterns = {
            'course_objectives': r'(?i)(course\s+objectives?|objectives?)[\s:]+([^#]+?)(?=\n\n|\Z)',
            'learning_outcomes': r'(?i)(learning\s+outcomes?|outcomes?)[\s:]+([^#]+?)(?=\n\n|\Z)',
            'course_content': r'(?i)(course\s+content|content|topics)[\s:]+([^#]+?)(?=\n\n|\Z)',
            'assessment': r'(?i)(assessment|grading|evaluation)[\s:]+([^#]+?)(?=\n\n|\Z)',
            'prerequisites': r'(?i)(prerequisites?|requirements?)[\s:]+([^#]+?)(?=\n\n|\Z)'
        }

        for section, pattern in patterns.items():
            match = re.search(pattern, text)
            if match:
                sections[section] = match.group(2).strip()

        return sections
