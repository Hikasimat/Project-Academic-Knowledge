"""
Authoritative Final Assessment Question Bank for Plus UAE × Vortexen AI Sales Academy.

CRITICAL SECURITY RULE:
The correct answer indices and grading criteria defined in this file must remain strictly on the backend.
API endpoints that serve questions to learners must strip the `correct_index` field.
"""

from typing import List, Dict, Any

ASSESSMENT_QUESTIONS: List[Dict[str, Any]] = [
    {
        "id": 1,
        "question": "A lead arrives at 9:10 PM. What do you do?",
        "options": [
            "Wait for the next working day",
            "Attempt prompt contact if permitted and call at an appropriate time; email and log all actions",
            "Send ten WhatsApp messages"
        ],
        "correct_index": 1,
        "rationale": "Operating Principle #5: Speed to lead with professional boundaries. Attempt prompt contact if permitted; otherwise email and log all actions immediately in CRM."
    },
    {
        "id": 2,
        "question": "You do not know whether a product is approved. What do you say?",
        "options": [
            "It is guaranteed",
            "I will verify the relevant system and return with documented confirmation by an agreed time",
            "Our competitor uses it"
        ],
        "correct_index": 1,
        "rationale": "Operating Principle #2: Truth & evidence. Never invent references or unsupported approvals. Commit to verified factual confirmation."
    },
    {
        "id": 3,
        "question": "The client prefers a phone call. What should be recorded?",
        "options": [
            "Nothing until contract",
            "Call and CRM note plus written email recap of key commitments",
            "Only a WhatsApp emoji"
        ],
        "correct_index": 1,
        "rationale": "Operating Principle #4: Document everything. Make the call, log the note in CRM, and send a written email recap of key commitments."
    },
    {
        "id": 4,
        "question": "An OEM requests exclusivity. What is the correct response?",
        "options": [
            "Promise immediately",
            "Agree verbally and revise later",
            "Discuss volume targets, territory and legal agreement before approval"
        ],
        "correct_index": 2,
        "rationale": "Commercial Governance: Exclusivity requires rigorous negotiation of volume targets, territory boundaries, and formal legal agreement approved by leadership."
    },
    {
        "id": 5,
        "question": "A purchase order is signed. What is the next gate?",
        "options": [
            "Declare project finished",
            "Validated operations handover and cost/payment baseline",
            "Stop updating CRM"
        ],
        "correct_index": 1,
        "rationale": "Workflow Gate 7-8: Contract handover requires validated operations handover, project scope review, and cost/payment baseline check."
    },
    {
        "id": 6,
        "question": "You contacted an ADNOC supplier prospect. What can you guarantee?",
        "options": [
            "Supplier registration success and purchase orders",
            "Nothing; describe verified process, documentation and conditional decisions",
            "A nuclear approval"
        ],
        "correct_index": 1,
        "rationale": "Plus UAE Pre-qualification Governance: Never guarantee committee decisions or tenders. Describe verified procedures, required documentation, and factual gates."
    },
    {
        "id": 7,
        "question": "What is the desired first-response SLA for inbound leads?",
        "options": [
            "Within 20 minutes, with immediate effort for high-intent leads",
            "Within two working days",
            "Only when the manager requests"
        ],
        "correct_index": 0,
        "rationale": "Operating Principle #5 & Automation Architecture: 20-minute response SLA for qualified inbound inquiries to maximize conversion."
    },
    {
        "id": 8,
        "question": "A prospect replies 'Not interested'. What follows?",
        "options": [
            "Send more automation",
            "Honor opt-out, stop relevant messages and update CRM",
            "Ask another employee to message"
        ],
        "correct_index": 1,
        "rationale": "Operating Principle #6 & #8: Protect the buyer and follow-up discipline. Honor opt-outs immediately, halt automated messaging, and update CRM status."
    },
    {
        "id": 9,
        "question": "Meeting ends without a decision. What must be created?",
        "options": [
            "A next action, owner, due date and emailed summary",
            "Nothing",
            "An invented contract value"
        ],
        "correct_index": 0,
        "rationale": "Sales Conduct: Every meeting must conclude with an agreed next action, designated owner, due date, and a formal emailed recap."
    },
    {
        "id": 10,
        "question": "You miss a promised callback. What is best?",
        "options": [
            "Ignore it",
            "Claim you called",
            "Acknowledge delay, provide correct update and new realistic time"
        ],
        "correct_index": 2,
        "rationale": "Operating Principle #3: Keep commitments with transparency. If delayed, acknowledge immediately, apologize, provide current status, and set a realistic new time."
    }
]

PASSING_THRESHOLD_PERCENT = 80.0
PASSING_MIN_CORRECT = 8
TOTAL_QUESTIONS = 10
