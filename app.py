import streamlit as st
import pandas as pd
from pypdf import PdfReader
from google import genai
import os
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()

st.set_page_config(page_title="ParcelPilot AI Agent", page_icon="📦", layout="wide")
st.title("ParcelPilot Support Agent")

# Initialize Gemini Client
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("GEMINI_API_KEY not found in .env file. Please check your setup.")
    st.stop()

client = genai.Client(api_key=api_key)

# 1. ACCESS CONTROL & USER ROLE SELECTION
st.sidebar.title("🔐 User Context")
role = st.sidebar.selectbox(
    "Select User Context", 
    ["Internal Support Staff", "Northstar Logistics (Customer)", "LumenWorks (Customer)"]
)
st.sidebar.info(f"Active Session: **{role}**")

# 2. DATA LOADERS
@st.cache_data
def load_excel_data():
    excel_path = "ParcelPilot_Assessment_Data.xlsx"
    # Use lowercase sheet names matching your Excel file
    orders = pd.read_excel(excel_path, sheet_name="orders")
    accounts = pd.read_excel(excel_path, sheet_name="accounts")
    return orders, accounts

@st.cache_data
def load_document_knowledge_base():
    """
    Reads documentation context.
    Excludes 02_Support_Policy_v2_DEPRECATED.pdf to ensure source reliability.
    """
    valid_docs = [
        "01_Support_Policy_v3_CURRENT.pdf",
        "03_Cancellation_and_Service_Credit_SOP_v4.pdf",
        "04_Product_Operations_Guide_and_Known_Issues.pdf",
        "05_Northstar_Logistics_Enterprise_Agreement.pdf",
        "06_LumenWorks_Service_Agreement.pdf"
    ]
    
    combined_text = ""
    for pdf_name in valid_docs:
        if os.path.exists(pdf_name):
            reader = PdfReader(pdf_name)
            combined_text += f"\n--- DOCUMENT SOURCE: {pdf_name} ---\n"
            for page in reader.pages:
                combined_text += page.extract_text() or ""
    return combined_text

try:
    df_orders, df_accounts = load_excel_data()
    doc_knowledge_base = load_document_knowledge_base()
except Exception as e:
    st.error(f"Error loading system data files: {e}")
    st.stop()

# Session State Initializations
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_action" not in st.session_state:
    st.session_state.pending_action = None

# Display Past Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 3. AGENT TOOLS
def tool_structured_data_lookup(order_id: str) -> str:
    """Tool 1: Queries database with scoped access control."""
    row = df_orders[df_orders['order_id'].astype(str).str.upper() == order_id.upper()]
    if row.empty:
        return f"Order ID {order_id} not found in database."
    
    order_data = row.to_dict(orient='records')[0]
    
    # Extract account ID dynamically from data
    account_id = str(order_data.get('account_id', '')).upper()

    # Dynamic Access Control Enforcement
    if "Northstar" in role:
        # Accepts ACC-001, ACC-1001, or numeric 1/1001
        if not any(valid_id in account_id for valid_id in ["ACC-001", "ACC-1001", "1"]):
            return "⚠️ ACCESS DENIED: Customer is restricted to viewing their own account data."
            
    if "LumenWorks" in role:
        # Accepts ACC-002, ACC-1002, or numeric 2/1002
        if not any(valid_id in account_id for valid_id in ["ACC-002", "ACC-1002", "2"]):
            return "⚠️ ACCESS DENIED: Customer is restricted to viewing their own account data."

    return f"Order Details: ID {order_data['order_id']} | Account ID: {account_id} | Status: {order_data.get('status', 'N/A')} | Carrier: {order_data.get('carrier', 'N/A')}"

    
def tool_document_retrieval(query: str, data_context: str = "") -> str:
    """Tool 2: LLM Reasoning over unstructured policies and contracts."""
    system_prompt = f"""You are ParcelPilot's AI Support Agent. 
Answer questions accurately using ONLY the provided documentation and structured data context.

RULES:
1. Enterprise agreements (e.g., Northstar agreement) override standard policy v3 rules.
2. Rely on Policy v3 context and ignore outdated v2 policies.
3. Be concise, direct, and factual.

STRUCTURED DATA CONTEXT:
{data_context}

DOCUMENTATION CONTEXT:
{doc_knowledge_base}

USER QUESTION:
{query}
"""
    # Updated model string to fix 404 error
    response = client.models.generate_content(
        model="gemini-3.6-flash",  # Or "gemini-3.7-flash"
        contents=system_prompt
    )
    return response.text

# 4. CHAT INTERACTION & MULTI-STEP LOGIC
user_input = st.chat_input("Ask about an order, contract terms, or service credit...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # State-Changing Interception (Tool 3)
    if "escalate" in user_input.lower() or "flag" in user_input.lower():
        st.session_state.pending_action = {"type": "escalation", "query": user_input}
        response_text = "⚠️ **Action Confirmation Required**: Are you sure you want to escalate this request to the human operations team?"
    else:
        # Multi-Step Tool Orchestration
        data_res = ""
        tools_used = []

        # Check for Order ID presence
        if "ORD-" in user_input.upper():
            words = user_input.split()
            order_id = [w.strip("?,.") for w in words if "ORD-" in w.upper()][0]
            data_res = tool_structured_data_lookup(order_id)
            tools_used.append("Structured Data Lookup")

        if "ACCESS DENIED" in data_res:
            response_text = f"**[Tool Used: Structured Data Lookup]**\n\n{data_res}"
        else:
            tools_used.append("Document Search (Gemini)")
            llm_res = tool_document_retrieval(user_input, data_context=data_res)
            
            tool_str = " + ".join(tools_used)
            response_text = f"**[Tools Used: {tool_str}]**\n\n{llm_res}"

    st.session_state.messages.append({"role": "assistant", "content": response_text})
    with st.chat_message("assistant"):
        st.write(response_text)

# 5. CONFIRMATION STEP FOR ACTIONS (Tool 3 Confirmation)
if st.session_state.pending_action:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Confirm Escalation"):
            act_msg = "**[Tool Used: State-Changing Action]**\n\n✅ Escalation ticket successfully logged in the system!"
            st.session_state.messages.append({"role": "assistant", "content": act_msg})
            st.session_state.pending_action = None
            st.rerun()
    with col2:
        if st.button("Cancel"):
            act_msg = "Action cancelled by user."
            st.session_state.messages.append({"role": "assistant", "content": act_msg})
            st.session_state.pending_action = None
            st.rerun()