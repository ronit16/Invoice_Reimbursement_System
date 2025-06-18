from fastapi import APIRouter, HTTPException
from app.models.models import ChatbotRequest, ChatbotResponse
from app.services.llm_service import LLMService
from app.services.vectore_store_service import VectorStoreService
from app.services.chat_session_manager import ChatSessionManager
from app.models.models import ReimbursementStatus
from app.core.prompts import FILTER_EXTRACTION_PROMPT
from logger import logger
import json
import re
router = APIRouter()
# Initialize services
llm_service = LLMService()
vector_store = VectorStoreService()
chat_manager = ChatSessionManager()

@router.post("/chatbot", response_model=ChatbotResponse)
async def chatbot_query(request: ChatbotRequest):
    """
    Endpoint for RAG chatbot to query invoice information
    
    Args:
        request: Chatbot request with query and optional session_id
    
    Returns:
        Chatbot response with retrieved information
    """
    
    try:

        filter_extraction_prompt = FILTER_EXTRACTION_PROMPT.format(query=request.query)
        filter_response = llm_service.model.generate_content(filter_extraction_prompt).text.strip()

        json_match = re.search(r'\{.*?\}', filter_response, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON found")
        try:
            extracted_filters = json.loads(json_match.group(0))
        except Exception as e:
            logger.error(f"Failed to parse LLM filters: {e}")
            extracted_filters = {}

        filters = {}
        if extracted_filters.get("employee_name"):
            filters["employee_name"] = extracted_filters["employee_name"]
        if extracted_filters.get("status"):
            filters["status"] = extracted_filters["status"]
        if extracted_filters.get("invoice_id"):
            filters["invoice_id"] = extracted_filters["invoice_id"]
        if extracted_filters.get("date"):
            filters["date"] = extracted_filters["date"]
        if extracted_filters.get("amount"):
            filters["amount"] = extracted_filters["amount"]

        # If session_id is not provided, create a new session
        if not request.session_id:
            request.session_id = chat_manager.create_session()

        logger.info("Filters extracted from LLM: %s", filters)
        # Search vector database
        search_results = vector_store.search_invoices(request.query, filters)
        
        # Format context from search results
        context = ""
        for result in search_results:
            metadata = result["metadata"]
            context += f"""
                    **Invoice ID:** {metadata.get('invoice_id', 'N/A')}
                    **Employee:** {metadata.get('employee_name', 'N/A')}
                    **Status:** {metadata.get('status', 'N/A')}
                    **Total Amount:** ${metadata.get('total_amount', 0):.2f}
                    **Approved Amount:** ${metadata.get('approved_amount', 0):.2f}
                    **Date:** {metadata.get('date', 'N/A')}

                    ---
                    """
        
        # Get chat history
        chat_history = chat_manager.get_session_history(request.session_id)
        
        # Generate response using LLM
        response_text = llm_service.generate_chatbot_response(
            request.query, context, chat_history
        )
        
        # Update chat history
        chat_manager.add_to_session(request.session_id, request.query, response_text)
        
        return ChatbotResponse(
            response=response_text,
            session_id=request.session_id
        )
        
    except Exception as e:
        logger.error(f"Error in chatbot endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))