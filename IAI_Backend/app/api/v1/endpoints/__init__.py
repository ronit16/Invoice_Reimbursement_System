from fastapi import APIRouter
from app.api.v1.endpoints import (
    analyze_invoices as  analyze_invoices_endpoint,
    chatbot as chatbot_endpoint,
)

router = APIRouter()
router.include_router(analyze_invoices_endpoint.router, prefix="/analyze-invoices", tags=["analyze-invoices"])
router.include_router(chatbot_endpoint.router, prefix="/chatbot", tags=["chatbot"])