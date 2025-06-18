from io import BytesIO
import PyPDF2
from app.utils.utils import clean_extracted_text
from logger import logger
from fastapi import HTTPException

class PDFProcessor:
    """Service for processing PDF documents"""
    
    @staticmethod
    def extract_text_from_pdf(pdf_content: bytes) -> str:
        """Extract text content from PDF bytes"""
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_content))
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return clean_extracted_text(text)
        except Exception as e:
            logger.error(f"Error extracting PDF text: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Error processing PDF: {str(e)}")