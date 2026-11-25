# Fintech Multi-Agent Customer Support System

An AI-powered fintech customer support automation system built using Python, FastAPI, and Google Gemini. The system uses five specialized AI agents to analyze support tickets, generate responses, prepare internal notes, and review response quality.

## 1. Problem Statement

Fintech customer support teams handle various customer issues, including failed payments, refund requests, wallet problems, KYC verification, transaction disputes, and account-related issues.

Handling these tickets manually can be time-consuming and may result in inconsistent responses.

This project demonstrates how a multi-agent AI workflow can automate ticket analysis and response preparation while maintaining human oversight for sensitive cases.

## 2. Project Objectives

- Automatically analyze incoming customer support tickets.
- Classify tickets based on category and priority.
- Identify potential financial and security risks.
- Generate customer-facing responses.
- Prepare internal support notes.
- Review AI-generated responses for accuracy and safety.
- Revise responses when the review identifies problems.
- Require human approval for sensitive cases.

## 3. Multi-Agent Architecture

The system consists of five specialized AI agents coordinated by a Python Workflow Orchestrator.

### Agent 1: Triage Agent

- Analyzes incoming customer support tickets.
- Identifies the ticket category.
- Assigns priority levels.
- Detects financial and security risks.
- Determines whether human approval is required.

### Agent 2: Draft Agent

- Generates customer-facing responses.
- Uses ticket information and triage results.
- Avoids making unsupported claims about transactions or refunds.

### Agent 3: Internal Note Agent

- Generates internal support notes.
- Summarizes the customer's issue.
- Provides relevant information for support staff.

### Agent 4: Review Agent

- Reviews generated customer responses.
- Checks accuracy and safety.
- Identifies unsupported claims.
- Determines whether the response is acceptable.

### Agent 5: Revision Agent

- Revises responses when the Review Agent identifies problems.
- The workflow allows one revision attempt.
- The revised response is reviewed again.

### Workflow Orchestrator

The Python Workflow Orchestrator coordinates all five agents and controls the execution sequence.

It also enforces human approval requirements for sensitive ticket categories and critical-priority cases.

## 4. Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.12 | Core programming language |
| FastAPI | Backend API framework |
| Google Gemini | Large Language Model |
| Google Gen AI SDK | Gemini API integration |
| Pydantic | Data validation |
| python-dotenv | Environment configuration |
| Pytest | Automated testing |
| Uvicorn | Application server |

## 5. Project Structure

```text
python-multi-agent-system/
│
├── app/
│   ├── agents/
│   │   ├── triage_agent.py
│   │   ├── draft_agent.py
│   │   ├── note_agent.py
│   │   ├── review_agent.py
│   │   └── revise_agent.py
│   │
│   ├── api/
│   │   └── ticket_routes.py
│   │
│   ├── models/
│   │   └── ticket.py
│   │
│   ├── services/
│   │   └── llm_service.py
│   │
│   ├── workflow/
│   │   └── orchestrator.py
│   │
│   ├── config.py
│   └── main.py
│
├── tests/
│   └── test_orchestrator.py
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## 6. Installation and Setup

### Prerequisites

- Python 3.12 or later
- Google Gemini API key
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/himanshuchoudharyyy/python-multi-agent-system.git
cd python-multi-agent-system
```

### Step 2: Create a Virtual Environment

```bash
python -m venv .venv
```

Activate the environment on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the project root directory.

You can use `.env.example` as a reference and add the following configuration:

```env
GEMINI_API_KEY=your_actual_gemini_api_key
GEMINI_MODEL=gemini-3.5-flash-lite
GEMINI_FALLBACK_MODEL=gemini-3.5-flash
```

Replace the API key placeholder with your actual Google Gemini API key.

The application uses:
- **Primary model:** Gemini 3.5 Flash Lite
- **Fallback model:** Gemini 3.5 Flash

The fallback model is used when the primary model encounters supported availability or quota errors.

**Important:** Never upload your `.env` file or expose your API key publicly. Only `.env.example` should be included in the repository.

### Step 5: Start the Application

```bash
uvicorn app.main:app --reload
```

The application will run at:

http://127.0.0.1:8000

## 7. API Endpoints

### 7.1 Health Check

**Method:** GET

**Endpoint:** `/api/v1/health`

Checks whether the application is running.

Example response:

```json
{
  "status": "healthy",
  "application": "Fintech Multi-Agent Support System"
}
```

### 7.2 Create and Process a Support Ticket

**Method:** POST

**Endpoint:** `/api/v1/tickets/`

Example request:

```json
{
  "ticket_id": "TICKET-001",
  "customer_id": "CUST-101",
  "customer_name": "John",
  "subject": "Payment deducted but transaction failed",
  "description": "Money was deducted from my wallet, but the merchant did not receive the payment.",
  "transaction_id": "TXN-12345",
  "transaction_amount": 1500.0
}
```

The ticket is processed through the multi-agent workflow.

The processing result includes ticket classification, priority, generated customer response, internal support note, review outcome, and human approval information.

### 7.3 Retrieve a Processed Ticket

**Method:** GET

**Endpoint:** `/api/v1/tickets/{ticket_id}`

Retrieves a previously processed ticket using its ticket ID.

## 8. API Documentation

After starting the application, access the interactive Swagger documentation:

http://127.0.0.1:8000/docs

Use Swagger UI to test the available API endpoints.

## 9. Human-in-the-Loop Approval

Financial and sensitive support cases require human oversight.

Examples include:

- Payment issues
- Refund requests
- Wallet issues
- Transaction disputes
- KYC issues
- Account-related issues
- Critical-priority tickets

The AI system prepares responses and identifies cases requiring human approval.

It does not independently execute refunds, reverse payments, or modify customer accounts.

## 10. Testing

Run the automated test suite using:

```bash
python -m pytest -v
```

## 11. Current Limitations

- Ticket data is stored temporarily in memory.
- Ticket records are not persistent across application restarts.
- A separate human approval interface is not currently implemented.
- The application does not directly execute financial transactions.
- Processing depends on the availability and usage limits of the configured Gemini API model.

## 12. Future Enhancements

- Database integration for persistent ticket storage.
- Customer support dashboard.
- Human approval interface.
- Ticket history and audit logging.
- Improved error handling and model availability management.
- Additional specialized AI agents.

## 13. Conclusion

This project demonstrates a practical multi-agent AI architecture for fintech customer support.

By assigning specialized responsibilities to individual agents and coordinating them through a Python orchestrator, the system demonstrates how AI can assist support teams with ticket classification, response generation, internal documentation, and response validation while maintaining human oversight for sensitive financial cases.