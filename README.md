# ParcelPilot AI Support Agent

An enterprise AI support agent prototype built for **ParcelPilot** (CalQuity Assessment). This system uses Streamlit, Pandas, PyPDF, and the Google Gemini API to process customer service queries, combine structured database metrics with unstructured policy documents, enforce role-based access control (RBAC), and require human confirmation for sensitive operations.

---

## Key Features & Capabilities

* **Multi-Step Reasoning:** Combines structured data lookups with unstructured PDF policy retrieval to handle complex edge cases.
* **Contract Precedence:** Ensures account-specific enterprise agreements override general standard operating procedure (SOP) policies.
* **Role-Based Access Control (RBAC):** Enforces data privacy constraints at the Python tool execution layer before sending context to the LLM.
* **Human-in-the-Loop Actions:** Requires explicit human approval before executing state-changing operations like ticket escalations.
* **Source Reliability:** Excludes deprecated policy files (`v2`) from vector indexing to prevent hallucinated or outdated policy responses.

---

## Tech Stack

* **Frontend:** Streamlit
* **LLM Engine:** Google Gemini API via `google-genai` SDK
* **Data Ingestion:** Pandas (Excel processing)
* **Document Parser:** PyPDF
* **Environment Management:** python-dotenv

---

## Project Structure

```text
ParcelPilot-AI-Agent/
├── app.py                            # Core Streamlit application & LLM tool orchestration
├── ParcelPilot_Assessment_Data.xlsx  # Orders & Tickets database
├── 01_Carrier_Delay_Policy_v3.pdf    # Active policy document
├── 02_Lost_Package_Standard_v1.pdf   # Active policy document
├── 03_High_Value_Claim_SOP_v1.pdf    # Active policy document
├── 04_Northstar_Agreement_v1.pdf     # Enterprise contract override
├── 05_LumenWorks_Agreement_v1.pdf    # Enterprise contract override
├── 06_International_Shipping_v1.pdf  # Active policy document
├── requirements.txt                  # Project dependencies
├── .env.example                      # Environment variables template
├── .gitignore                        # Git exclusion rules
└── README.md                         # Documentation
```

## Getting Started Locally
1. Prerequisites
Ensure you have Python 3.10+ installed on your system.

2. Clone the Repository
```git clone [https://github.com/mrugakshiharkare/ParcelPilot-AI-Agent.git](https://github.com/mrugakshiharkare/ParcelPilot-AI-Agent.git)```
```cd ParcelPilot-AI-Agent```

3. Set Up Virtual Environment
```python -m venv venv```
- Windows: venv\Scripts\activate
- macOS/Linux: source venv/bin/activate

4. Install Dependencies
```pip install -r requirements.txt```

5. Configure API Key
Create a .env file in the root directory:   
~Code snippet`
GEMINI_API_KEY=your_actual_gemini_api_key_here

6. Run the Application
```streamlit run app.py```

## System Design & Tool Architecture
1. Structured Data Lookup (tool_structured_data_lookup): Queries ParcelPilot_Assessment_Data.xlsx to pull live order and ticket information using strict Account ID filters.

2. Unstructured Retrieval (tool_document_retrieval): Ingests PDF policies into memory, stripping out deprecated files (Policy v2), and passes relevant context to Gemini for reasoning.

3. Escalation Engine (tool_escalate_ticket): Flags high-priority or unresolved tickets with an interactive human confirmation UI step before committing state changes.

## Access Control & Guardrails
- Internal Support Staff: Full visibility across all accounts and ticket histories.
- Customer Accounts (Northstar / LumenWorks): Strictly scoped to their respective Account IDs. Queries requesting data outside their assigned scope return an explicit ⚠️ ACCESS DENIED response directly at the Python tool boundary.

## Architecture Note

* **Agent & Tool Design:** Constructed a tool-calling AI agent using Streamlit and the `google-genai` SDK (`gemini-3.6-flash`). The core orchestration layer routes user queries dynamically across three modular Python tools:
  1. `tool_structured_data_lookup`: Performs Pandas queries on Excel order/ticket data.
  2. `tool_document_retrieval`: Searches indexed PDF knowledge base files using PyPDF text extraction.
  3. `tool_escalate_ticket`: Triggers state-changing ticket escalations with human confirmation UI guardrails.
* **Document & Structured-Data Handling:** Structured Excel records are queried dynamically using dataframe filtering. Unstructured PDF policies are ingested into memory during startup and filtered based on relevance to the user's query.
* **Source Reliability & Conflict Handling:** Solved source conflicts by programmatically filtering out `02_Support_Policy_v2_DEPRECATED.pdf` during startup to ensure active policy precedence (`Policy v3`). Applied account-specific enterprise contract overrides (`Northstar` / `LumenWorks` SLAs) over general SOP policies.
* **Access Control Guardrails:** Role-Based Access Control (RBAC) is enforced in Python at the tool execution layer. If a customer role attempts to query data belonging to another account, the tool immediately halts execution and returns an `⚠️ ACCESS DENIED` alert before passing context to the LLM.
* **Major Technical Trade-Offs:** Chose in-memory PDF parsing via PyPDF instead of a dedicated vector database (e.g., Pinecone/Chroma). This minimized infrastructure complexity and latency for a zero-cost prototype while maintaining instant lookups over small policy sets.

---

## Product Note

* **Selected Additional Problem:** Problem 1 — Proactive Issue Detection.
* **Proposed Solution:** Implemented an automated background check that continuously scans carrier delay metrics across active orders. When repeated carrier delays exceed defined thresholds for an account, the system proactively surfaces an alert to support agents before the customer logs a ticket.
* **Future Work for ParcelPilot:** 
  1. Automated carrier claims filing integration via webhooks.
  2. Multi-channel integration (Slack/Zendesk) for real-time support team notifications.
* **Intentionally Left Out:** Omitted persistent external database hosting (e.g., PostgreSQL) and OAuth2 user authentication, opting for Streamlit session-state role switching and Excel-based lookups to keep the architecture lightweight and zero-maintenance.
* **Key Success Metric:** **First Contact Resolution (FCR) Rate** — measuring the percentage of tier-1 support queries resolved instantly without requiring manual human agent intervention.

---

## AI Tool Usage

* **AI Coding Tools Used:** Google Gemini (Gemini 2.5 Flash / Gemini 2.0 Thinking).
* **Usage Details:** Used for step-by-step technical architecture planning, writing Streamlit layout components, drafting tool function signatures, configuring `.env` variable handling, and debugging Git repository deployment workflows.
