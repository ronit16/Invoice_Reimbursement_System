from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.pdf_processor import PDFProcessor
from app.services.llm_service import LLMService
from app.services.vectore_store_service import VectorStoreService
from app.services.chat_session_manager import ChatSessionManager
import tempfile
import zipfile
from io import BytesIO
from pathlib import Path
from datetime import datetime
from logger import logger
from app.models.models import InvoiceAnalysisResponse

router = APIRouter()

# Initialize services
pdf_processor = PDFProcessor()
llm_service = LLMService()
vector_store = VectorStoreService()
chat_manager = ChatSessionManager()

@router.post("/analyze-invoices")
async def analyze_invoices(
    employee_name: str = Form(...),
    policy_file: UploadFile = File(...),
    invoices_zip: UploadFile = File(...)
    ):
    """
    Endpoint to analyze employee invoices against company policy
    
    Args:
        employee_name: Name of the employee
        policy_file: PDF file containing HR reimbursement policy
        invoices_zip: ZIP file containing invoice PDFs
    
    Returns:
        JSON response with analysis results
    """

    try:

        if not policy_file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Policy file must be a PDF")
        
        if not invoices_zip.filename.endswith('.zip'):
            raise HTTPException(status_code=400, detail="Invoices file must be a ZIP archive")
        
        policy_content = await policy_file.read()
        policy_content = pdf_processor.extract_text_from_pdf(policy_content)

        invoices_content = await invoices_zip.read()
        invoices_processed = 0
        errors = []

        with tempfile.TemporaryDirectory() as temp_dir:
            with zipfile.ZipFile(BytesIO(invoices_content), 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            for file_path in Path(temp_dir).rglob("*.pdf"):
                try:
                    invoice_content = pdf_processor.extract_text_from_pdf(file_path.read_bytes())

                    analysis_result = llm_service.analyze_invoice(invoice_content, policy_content, employee_name)
                    
                    employee_name = employee_name.replace(" ", "_").lower()
                    # Generate unique invoice ID
                    invoice_id = f"{employee_name}_{file_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

                    success = vector_store.store_invoice_analysis(
                        invoice_id, invoice_content, analysis_result, employee_name
                    )

                    if success:
                        invoices_processed += 1
                    else:
                        errors.append(f"Failed to store analysis for {file_path.name}")

                except Exception as e:
                    error_msg = f"Error processing {file_path.name}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)

        return InvoiceAnalysisResponse(
                status="success" if invoices_processed > 0 else "partial_success",
                message=f"Successfully processed {invoices_processed} invoice(s)",
                invoices_processed=invoices_processed,
                errors=errors
            )

    except Exception as e:
        logger.error(f"Error in analyze_invoices endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))