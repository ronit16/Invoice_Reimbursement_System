
ANALYSE_INVOICE_PROMPT = """
You are an expert financial analyst. Analyze the following employee invoice against the company reimbursement policy.
COMPANY POLICY:
{policy_text} 
EMPLOYEE INVOICE:
Employee: {employee_name}
Invoice Content: {invoice_text}
Based on the policy, determine:
1. Reimbursement Status: "Fully Reimbursed", "Partially Reimbursed", or "Declined"
2. Detailed reason for the status
3. If partially reimbursed, specify the approved amount
Provide a structured JSON response only with no extra response with the following fields:
```json
{{
    "status": "ReimbursementStatus",
    "reason": "string",
    "approved_amount": "float",
    "total_amount": "float"
}}
"""

CHATBOT_RESPONSE_PROMPT = """
You are a helpful assistant for an invoice reimbursement system.
Answer the user's query based on the provided context from the invoice database.
CHAT HISTORY:
{history_text}
CONTEXT FROM INVOICE DATABASE:
{context}
USER QUERY: {query}
Provide a helpful response in markdown format. If no relevant information is found,
say so politely and suggest what information might be helpful.
"""


FILTER_EXTRACTION_PROMPT = """
You are an intelligent assistant that extracts structured filters from employee invoice reimbursement queries.

USER QUERY:
"{query}"

Extract and return a structured JSON with the following fields (if mentioned):
- "employee_name": string (lower case and replace space with _ (underscore) ) or null
- "status": one of ["Fully Reimbursed", "Partially Reimbursed", "Declined"] or null
- "invoice_id": string or null
- "date": exact string in "YYYY-MM-DD" format or approximate like "May 2024" or null
- "amount": float or approximate if mentioned (e.g., "around 150") or null

Return only valid JSON like this:
```json
{{
  "employee_name": "ronit_shah",
  "status": "Fully Reimbursed",
  "invoice_id": null,
  "date": "May 2024",
  "amount": 150
}}
"""
