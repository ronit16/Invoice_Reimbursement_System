import streamlit as st
import requests
import json
import uuid
from datetime import datetime
import time
from typing import Dict, List, Any

# Configuration
API_BASE_URL = "http://localhost:8000"  # Adjust this to your FastAPI server URL

# Page configuration
st.set_page_config(
    page_title="Invoice Analysis & Chatbot",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .success-box {
        padding: 1rem;
        border-radius: 10px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    
    .error-box {
        padding: 1rem;
        border-radius: 10px;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        margin: 1rem 0;
    }
    
    .chat-container {
        max-height: 400px;
        overflow-y: auto;
        padding: 1rem;
        border: 1px solid #ddd;
        border-radius: 10px;
        background-color: #f8f9fa;
    }
    
    .user-message {
        background-color: #007bff;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        text-align: right;
        margin-left: 20%;
    }
    
    .bot-message {
        background-color: #e9ecef;
        color: #333;
        padding: 0.5rem 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        margin-right: 20%;
    }
    
    .invoice-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: #fff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .status-approved {
        color: #28a745;
        font-weight: bold;
    }
    
    .status-rejected {
        color: #dc3545;
        font-weight: bold;
    }
    
    .status-partial {
        color: #fd7e14;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_session_id' not in st.session_state:
    st.session_state.chat_session_id = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None

def create_new_chat_session():
    """Create a new chat session"""
    st.session_state.chat_session_id = str(uuid.uuid4())
    st.session_state.chat_history = []
    st.success("New chat session created!")

def format_status_color(status: str) -> str:
    """Return CSS class based on status"""
    status_lower = status.lower()
    if 'approved' in status_lower or 'reimbursed' in status_lower:
        return 'status-approved'
    elif 'rejected' in status_lower or 'denied' in status_lower:
        return 'status-rejected'
    else:
        return 'status-partial'

def display_invoice_analysis_results(results: Dict[str, Any]):
    """Display invoice analysis results in a formatted way"""
    st.subheader("📊 Analysis Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Status", results.get('status', 'Unknown'))
    
    with col2:
        st.metric("Invoices Processed", results.get('invoices_processed', 0))
    
    with col3:
        if results.get('errors'):
            st.metric("Errors", len(results['errors']))
        else:
            st.metric("Errors", 0)
    
    # Success message
    if results.get('status') == 'success':
        st.markdown(f"""
        <div class="success-box">
            <strong>✅ Success!</strong><br>
            {results.get('message', 'Analysis completed successfully')}
        </div>
        """, unsafe_allow_html=True)
    
    # Display errors if any
    if results.get('errors'):
        st.subheader("⚠️ Errors Encountered")
        for error in results['errors']:
            st.markdown(f"""
            <div class="error-box">
                <strong>Error:</strong> {error}
            </div>
            """, unsafe_allow_html=True)

def send_chatbot_query(query: str, session_id: str = None) -> Dict[str, Any]:
    """Send query to chatbot API"""
    try:
        payload = {
            "query": query,
            "session_id": session_id
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/chatbot/chatbot",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "response": f"Error: {response.status_code} - {response.text}",
                "session_id": session_id
            }
    except Exception as e:
        return {
            "response": f"Connection error: {str(e)}",
            "session_id": session_id
        }

def display_chat_history():
    """Display chat history in a formatted way"""
    if st.session_state.chat_history:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        for chat in st.session_state.chat_history:
            # User message
            st.markdown(f"""
            <div class="user-message">
                <strong>You:</strong> {chat['user']}
            </div>
            """, unsafe_allow_html=True)
            
            # Bot message
            st.markdown(f"""
            <div class="bot-message">
                <strong>Assistant:</strong> {chat['bot']}
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No chat history yet. Start a conversation!")

# Main App Header
st.markdown('<h1 class="main-header">📄 Invoice Analysis & AI Assistant</h1>', unsafe_allow_html=True)

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.selectbox(
    "Choose a feature:",
    ["Invoice Analysis", "AI Chatbot", "About"]
)

# Invoice Analysis Page
if page == "Invoice Analysis":
    st.header("📤 Upload & Analyze Invoices")
    
    with st.form("invoice_analysis_form"):
        st.subheader("Upload Files")
        
        # Employee name input
        employee_name = st.text_input(
            "Employee Name *",
            placeholder="Enter employee name",
            help="Name of the employee whose invoices are being analyzed"
        )
        
        # Policy file upload
        policy_file = st.file_uploader(
            "Upload HR Policy (PDF) *",
            type=['pdf'],
            help="Upload the company's reimbursement policy document"
        )
        
        # Invoice files upload
        invoice_zip = st.file_uploader(
            "Upload Invoice Archive (ZIP) *",
            type=['zip'],
            help="Upload a ZIP file containing all invoice PDFs"
        )
        
        # Submit button
        submit_button = st.form_submit_button("🔍 Analyze Invoices")
        
        if submit_button:
            if not employee_name:
                st.error("Please enter employee name")
            elif not policy_file:
                st.error("Please upload a policy PDF file")
            elif not invoice_zip:
                st.error("Please upload a ZIP file containing invoices")
            else:
                with st.spinner("Analyzing invoices... This may take a few minutes."):
                    try:
                        # Prepare files for API request
                        files = {
                            "policy_file": (policy_file.name, policy_file.getvalue(), "application/pdf"),
                            "invoices_zip": (invoice_zip.name, invoice_zip.getvalue(), "application/zip")
                        }
                        
                        data = {
                            "employee_name": employee_name
                        }
                        
                        # Send request to API
                        response = requests.post(
                            f"{API_BASE_URL}/api/v1/analyze-invoices/analyze-invoices",
                            files=files,
                            data=data
                        )
                        
                        if response.status_code == 200:
                            results = response.json()
                            st.session_state.analysis_results = results
                            display_invoice_analysis_results(results)
                        else:
                            st.error(f"Analysis failed: {response.status_code} - {response.text}")
                    
                    except Exception as e:
                        st.error(f"Error connecting to analysis service: {str(e)}")
    
    # Display previous results if available
    if st.session_state.analysis_results:
        st.divider()
        st.subheader("📋 Previous Analysis Results")
        display_invoice_analysis_results(st.session_state.analysis_results)

# AI Chatbot Page
elif page == "AI Chatbot":
    st.header("🤖 AI Invoice Assistant")
    
    # Chat session management
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if st.session_state.chat_session_id:
            st.success(f"Active Session: {st.session_state.chat_session_id[:8]}...")
        else:
            st.info("No active chat session")
    
    with col2:
        if st.button("🆕 New Session"):
            create_new_chat_session()
    
    with col3:
        if st.button("🗑️ Clear History"):
            st.session_state.chat_history = []
            st.success("Chat history cleared!")
    
    st.divider()
    
    # Chat interface
    st.subheader("💬 Chat with AI Assistant")
    
    # Display chat history
    display_chat_history()
    
    # Query input
    with st.form("chat_form", clear_on_submit=True):
        user_query = st.text_input(
            "Ask me about invoices:",
            placeholder="e.g., Show me rejected invoices for John Doe, or What invoices were processed in May 2024?",
            help="You can ask about specific employees, dates, amounts, or invoice statuses"
        )
        submit_chat = st.form_submit_button("💬 Send")
        
        if submit_chat and user_query:
            if not st.session_state.chat_session_id:
                create_new_chat_session()
            
            with st.spinner("Getting response..."):
                # Send query to chatbot
                response = send_chatbot_query(user_query, st.session_state.chat_session_id)
                
                # Update session state
                if response.get('session_id'):
                    st.session_state.chat_session_id = response['session_id']
                
                # Add to chat history
                chat_entry = {
                    'user': user_query,
                    'bot': response.get('response', 'Sorry, I could not process your request.'),
                    'timestamp': datetime.now().isoformat()
                }
                st.session_state.chat_history.append(chat_entry)
                
                # Refresh the page to show new message
                st.rerun()
    
    # Quick action buttons
    st.subheader("🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Show All Invoices"):
            if not st.session_state.chat_session_id:
                create_new_chat_session()
            
            response = send_chatbot_query("Show me all processed invoices", st.session_state.chat_session_id)
            chat_entry = {
                'user': "Show me all processed invoices",
                'bot': response.get('response', 'Sorry, I could not process your request.'),
                'timestamp': datetime.now().isoformat()
            }
            st.session_state.chat_history.append(chat_entry)
            st.rerun()
    
    with col2:
        if st.button("❌ Show Rejected"):
            if not st.session_state.chat_session_id:
                create_new_chat_session()
            
            response = send_chatbot_query("Show me all rejected invoices", st.session_state.chat_session_id)
            chat_entry = {
                'user': "Show me all rejected invoices",
                'bot': response.get('response', 'Sorry, I could not process your request.'),
                'timestamp': datetime.now().isoformat()
            }
            st.session_state.chat_history.append(chat_entry)
            st.rerun()
    
    with col3:
        if st.button("✅ Show Approved"):
            if not st.session_state.chat_session_id:
                create_new_chat_session()
            
            response = send_chatbot_query("Show me all approved invoices", st.session_state.chat_session_id)
            chat_entry = {
                'user': "Show me all approved invoices",
                'bot': response.get('response', 'Sorry, I could not process your request.'),
                'timestamp': datetime.now().isoformat()
            }
            st.session_state.chat_history.append(chat_entry)
            st.rerun()

# About Page
elif page == "About":
    st.header("ℹ️ About This Application")
    
    st.markdown("""
    ## 📄 Invoice Analysis & AI Assistant
    
    This application provides comprehensive invoice analysis and intelligent querying capabilities.
    
    ### 🔧 Features:
    
    #### 📤 Invoice Analysis
    - Upload employee invoices in ZIP format
    - Upload company reimbursement policy (PDF)
    - Automated analysis using AI
    - Detailed results with approval status
    - Error reporting and handling
    
    #### 🤖 AI Chatbot
    - Natural language queries about invoices
    - Session-based conversation history
    - Filter by employee, date, amount, status
    - Quick action buttons for common queries
    - Intelligent context-aware responses
    
    ### 🎯 How to Use:
    
    1. **Invoice Analysis**: Upload your policy document and invoice ZIP file, then click analyze
    2. **AI Chatbot**: Ask questions about processed invoices using natural language
    
    ### 🔍 Example Queries:
    - "Show me all invoices for John Doe"
    - "What invoices were rejected in May 2024?"
    - "Find invoices with amounts over $500"
    - "Show me partially approved invoices"
    
    ### 🛠️ Technical Stack:
    - **Frontend**: Streamlit
    - **Backend**: FastAPI
    - **AI/ML**: Google Gemini, Sentence Transformers
    - **Vector Database**: ChromaDB
    - **PDF Processing**: PyPDF2
    
    ### 📞 Support:
    For technical support or feature requests, please contact the development team.
    """)
    
    # # System status
    # st.subheader("🔧 System Status")
    
    # try:
    #     # Test API connection
    #     response = requests.get(f"{API_BASE_URL}/health", timeout=5)
    #     if response.status_code == 200:
    #         st.success("✅ API Service: Online")
    #     else:
    #         st.error(f"❌ API Service: Error ({response.status_code})")
    # except:
    #     st.error("❌ API Service: Offline")
    
    # Configuration info
    st.subheader("⚙️ Configuration")
    st.info(f"API Endpoint: {API_BASE_URL}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>Invoice Analysis & AI Assistant | Built with ❤️ using Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True
)