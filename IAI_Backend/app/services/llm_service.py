from typing import Dict, Any, List
from logger import logger
import json
import re
# from huggingface_hub import hf_hub_download
import google.generativeai as genai
from dotenv import load_dotenv
from app.core.prompts import ANALYSE_INVOICE_PROMPT, CHATBOT_RESPONSE_PROMPT
from app.models.models import ReimbursementStatus
import os

load_dotenv()

class LLMService:
    """Service for LLM operations using Hugging Face transformers"""
    
    def __init__(self):
        try:
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            self.model = genai.GenerativeModel("gemini-2.5-flash-preview-05-20")
        except Exception as e:
            logger.error(f"Failed to configure LLM service: {str(e)}")


    def analyze_invoice(self, invoice_text: str, policy_text: str, employee_name: str) -> Dict[str, Any]:
        """Analyze invoice against policy using LLM"""

        try:
            if not self.model:
                raise RuntimeError("LLM model not available")
            prompt = ANALYSE_INVOICE_PROMPT.format(
                policy_text=policy_text,
                employee_name=employee_name,
                invoice_text=invoice_text
            )
            response = self.model.generate_content(prompt).text.strip()
            return self._parse_analysis_response(response)
        except Exception as e:
            logger.error(f"Error in LLM analysis: {str(e)}")
            return None

    def _parse_analysis_response(self, analysis_text: str) -> Dict[str, Any]:
        """Parse LLM response into structured format"""

        try:
            json_match = re.search(r'\{.*?\}', analysis_text, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON found")
            analysis_data = json.loads(json_match.group(0))
            return {
                "status": analysis_data.get("status", ReimbursementStatus.PARTIALLY_REIMBURSED),
                "reason": analysis_data.get("reason", "No reason provided"),
                "approved_amount": float(analysis_data.get("approved_amount", 0.0)),
                "total_amount": float(analysis_data.get("total_amount", 0.0))
            }
        except json.JSONDecodeError:
            logger.error("Failed to parse LLM response as JSON")
            return None

    def generate_chatbot_response(self, query: str, context: str, chat_history: List[Dict]) -> str:
        """Generate chatbot response based on query and retrieved context"""
        
        try:
            history_text = ""
            for msg in chat_history[-3:]:
                history_text += f"User: {msg.get('user', '')}\nBot: {msg.get('bot', '')}\n"

            if not self.model:
                raise RuntimeError("LLM model not available")

            prompt = CHATBOT_RESPONSE_PROMPT.format(
                        history_text=history_text, 
                        context=context, 
                        query=query
                    )
            return self.model.generate_content(prompt).text.strip()
        except Exception as e:
            logger.error(f"Error generating chatbot response: {str(e)}")
            return "Sorry, I couldn't process your request at the moment."