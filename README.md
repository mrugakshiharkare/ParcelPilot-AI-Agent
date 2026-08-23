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
* **LLM Engine:** Google Gemini (`gemini-2.5-flash`) via `google-genai` SDK
* **Data Ingestion:** Pandas (Excel processing)
* **Document Parser:** PyPDF
* **Environment Management:** python-dotenv

---

## Project Structure

```text
ParcelPilot-AI-Agent/
├── app.py                           # Core Streamlit application & LLM tool orchestration
├── ParcelPilot_Assessment_Data.xlsx  # Orders & Tickets database
├── 01_Carrier_Delay_Policy_v3.pdf   # Active policy document
├── 02_Lost_Package_Standard_v1.pdf  # Active policy document
├── 03_High_Value_Claim_SOP_v1.pdf   # Active policy document
├── 04_Northstar_Agreement_v1.pdf    # Enterprise contract override
├── 05_LumenWorks_Agreement_v1.pdf   # Enterprise contract override
├── 06_International_Shipping_v1.pdf # Active policy document
├── requirements.txt                 # Project dependencies
├── .env.example                     # Environment variables template
├── .gitignore                       # Git exclusion rules
└── README.md                        # Documentation


## Getting Started Locally

### 1. Prerequisites
Ensure you have **Python 3.10+** installed on your system.

### 2. Clone the Repository
```bash
git clone [https://github.com/mrugakshiharkare/ParcelPilot-AI-Agent.git](https://github.com/mrugakshiharkare/ParcelPilot-AI-Agent.git)
cd ParcelPilot-AI-Agent
