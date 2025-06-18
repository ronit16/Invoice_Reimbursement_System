from typing import List, Optional
from pydantic import BaseModel

class ReimbursementStatus:
    FULLY_REIMBURSED = "Fully Reimbursed"
    PARTIALLY_REIMBURSED = "Partially Reimbursed"
    DECLINED = "Declined"

class InvoiceAnalysisRequest(BaseModel):
    employee_name: str

class ChatbotRequest(BaseModel):
    query: str
    session_id: Optional[str] = "default"

class InvoiceAnalysisResponse(BaseModel):
    status: str
    message: str
    invoices_processed: int
    errors: List[str] = []

class ChatbotResponse(BaseModel):
    response: str
    session_id: str