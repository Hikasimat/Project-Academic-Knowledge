"""
Course definitions and 15-day sequential learning syllabus.
Directly derived from the Plus UAE × Vortexen source material.
Structured into the 6 sequential sections of the unified master course:
"Specialized Sales Reference Catalogs & Practical Toolkits"
"""

from typing import List, Dict, Any

COURSE_TRACKS: List[Dict[str, Any]] = [
    {
        "code": "specialized_toolkits",
        "track_name": "Specialized Sales Reference Catalogs & Practical Toolkits",
        "title": "Specialized Sales Reference Catalogs & Practical Toolkits",
        "description": "Unified 6-section master sales academy merging Plus UAE corporate advisory, Vortexen certified passive fire protection engineering, buyer committee mapping, B2B AI prompt workflows, live GCC case studies, and CRM funnel discipline."
    },
    {
        "code": "foundation",
        "track_name": "Both companies — Foundation",
        "title": "Plus UAE × Vortexen — Sales Academy (Foundation)",
        "description": "Comprehensive sales training across both Plus UAE business setup & PRO advisory and Vortexen passive fire protection & technical coatings. Covers ethical selling, market mapping, AI-assisted outreach, and deal governance."
    },
    {
        "code": "plus_sales",
        "track_name": "Plus UAE — Sales",
        "title": "Plus UAE — Corporate & Market Entry Sales Track",
        "description": "Specialized curriculum for Plus UAE corporate advisory, mainland & freezone company formation, ADNOC/utility vendor registration, PRO operations, and international OEM representation."
    },
    {
        "code": "vortexen_tech",
        "track_name": "Vortexen — Technical Sales",
        "title": "Vortexen — Passive Fire Protection Technical Sales Track",
        "description": "Specialized curriculum for Vortexen technical sales, certified passive fire protection (PFP), cable coating, structural fireproofing, BOQ takeoffs, Civil Defence compliance, and project handover."
    }
]

FIFTEEN_DAY_SYLLABUS: List[Dict[str, Any]] = [
    # SECTION 1: Plus UAE Service Catalog (Lessons 1 to 5)
    {
        "day_number": 1,
        "step_number": 1,
        "section_number": 1,
        "section_title": "Plus UAE Service Catalog",
        "title": "Company positioning; ethics and honesty",
        "description": "Master core operating principles: politeness, evidence-based claims, absolute honesty regarding capabilities, and zero tolerance for invented references.",
        "target_section": "plus",
        "topics": [
            "Politeness & Executive Trust: Respect for client time, consultative inquiry, long-term advisor positioning",
            "Truth & Evidence Discipline: Strictly zero tolerance for fabricated references or unauthorized approvals",
            "Delivery Commitment Guardrails: Never promise what operational teams cannot execute",
            "Audit & CRM Trail: Mandatory call recaps and written audit records for every stakeholder interaction"
        ]
    },
    {
        "day_number": 2,
        "step_number": 2,
        "section_number": 1,
        "section_title": "Plus UAE Service Catalog",
        "title": "Plus UAE business setup & market entry",
        "description": "Explore Abu Dhabi mainland and free zone setup, licensing, operational requirements, and target customer personas for foreign OEMs and entrants.",
        "target_section": "plus",
        "topics": [
            "Abu Dhabi Mainland Licensing: DED activity classifications, commercial registrations, and 100% foreign ownership criteria",
            "Free Zone Ecosystems: ADGM, Masdar City, KIZAD/KEZAD selection criteria and branch establishment",
            "Foreign OEM Personas: European, North American, and Asian industrial entrants seeking regional foothold",
            "Post-Licensing Operations: Chamber of Commerce registration, establishment cards, and statutory compliance"
        ]
    },
    {
        "day_number": 3,
        "step_number": 3,
        "section_number": 1,
        "section_title": "Plus UAE Service Catalog",
        "title": "Plus UAE PRO, immigration and tax boundaries",
        "description": "Understand employment visas, quota systems, corporate tax boundaries, and compliant administrative processes for multinational clients.",
        "target_section": "plus",
        "topics": [
            "Outsourced PRO Operations: Quota approvals, MOHRE labor contracts, and residence visa lifecycle",
            "Executive Investor & Golden Visas: Eligibility criteria, processing documentation, and family sponsorship",
            "Corporate Tax & VAT Boundaries: Tax registration requirements, filing calendars, and boundary of advisory vs. legal opinion",
            "Workforce Mobilization: CICPA site access security clearances and oilfield pass coordination"
        ]
    },
    {
        "day_number": 4,
        "step_number": 4,
        "section_number": 1,
        "section_title": "Plus UAE Service Catalog",
        "title": "ADNOC/ENEC/utility prequalification reality",
        "description": "Learn realistic supplier prequalification timelines, ICV requirements, vendor portal mechanics, and why registration cannot be promised as a guarantee.",
        "target_section": "plus",
        "topics": [
            "ADNOC Supplier Registration Mechanics: Vendor portal onboarding, document checklists, and commercial review stages",
            "In-Country Value (ICV) Reality: Weighting factors, certified auditor requirements, and scoring impact on bids",
            "ENEC & Utility Gates: Nuclear QA supply chain requirements (Nawah ecosystem) vs. TAQA/DEWA/SEWA registrations",
            "Sales Communication Rules: Crucial distinction between supplier registration, prequalification, and project award"
        ]
    },
    {
        "day_number": 5,
        "step_number": 5,
        "section_number": 1,
        "section_title": "Plus UAE Service Catalog",
        "title": "Representation and OEM commercial terms",
        "description": "Analyze agency agreements, distributor representation, exclusivity conditions, territory bounds, and commercial risk mitigation.",
        "target_section": "plus",
        "topics": [
            "Commercial Agency Agreements: Commercial representation models, territory exclusivity, and margin defense",
            "Risk Allocation: Product liability, warranty back-to-back pass-through, and inventory commitments",
            "Pilot Pipeline Milestones: Setting objective conversion milestones before granting long-term representation rights",
            "Section 1 Knowledge Exam: Verification of Abu Dhabi corporate advisory competencies and compliance rules"
        ]
    },

    # SECTION 2: Vortexen Technical Services (Lessons 6 to 7)
    {
        "day_number": 6,
        "step_number": 6,
        "section_number": 2,
        "section_title": "Vortexen Technical Services",
        "title": "Vortexen firestopping and fire system reading",
        "description": "Study passive fire protection fundamentals, penetrations, MEP drawings, Civil Defence approvals, and certified firestop installation methods.",
        "target_section": "vortexen",
        "topics": [
            "Passive Fire Protection (PFP) Fundamentals: Compartmentation, F-ratings, T-ratings, and smoke containment",
            "MEP Drawings & Penetration Reading: Identifying pipe, cable tray, busduct, and damper penetrations across wall/floor assemblies",
            "Listed Tested Assemblies: Selecting verified UL, FM, and BS EN systems matching substrate and annular space limits",
            "Civil Defence Compliance: Material submittals, testing laboratory reports, and statutory inspection protocols"
        ]
    },
    {
        "day_number": 7,
        "step_number": 7,
        "section_number": 2,
        "section_title": "Vortexen Technical Services",
        "title": "Cable coating, fireproofing, joints and coatings",
        "description": "Examine intumescent coatings, structural steel fireproofing, electrical cable flame-retardant coatings, and industrial protective finishes.",
        "target_section": "vortexen",
        "topics": [
            "Structural Steel Fireproofing: Intumescent coating dry film thickness (DFT) calculations based on Hp/A section factors",
            "Cable Fire-Retardant Coating: Power stations, substations, and industrial tray flame-propagation protection",
            "Fire-Rated Movement Joints: Floor-to-floor, curtain wall perimeter, and seismic joint UL tested assemblies",
            "Quality Control & Handover: DFT gauge measurement, holiday testing, defect registers, and Civil Defence certification"
        ]
    },

    # SECTION 3: Markets & Buyer Committee Map (Lessons 8 to 9)
    {
        "day_number": 8,
        "step_number": 8,
        "section_number": 3,
        "section_title": "Markets & Buyer Committee Map",
        "title": "ICP, sectors, decision-makers and scoring",
        "description": "Map ideal customer profiles (ICPs), target sectors in UAE & KSA, decision-maker personas, and practice objective prospect scoring.",
        "target_section": "targets",
        "topics": [
            "Priority Regional Sectors: Oil & Gas, Nuclear & Power, Building MEP, Marine Yards, and Exporter OEMs",
            "Buying Committee Triad: Economic Buyer (CFO/GM), Technical Buyer (QA/Consultant), Process Buyer (Procurement/Admin)",
            "0-100 Prospect Scoring Matrix: Evaluating service fit, funded signals, decision-maker access, timing, and margin",
            "Lead Triage Rules: Grade A (immediate 20-min call), Grade B (nurture & research), Grade C (passive monitoring)"
        ]
    },
    {
        "day_number": 9,
        "step_number": 9,
        "section_number": 3,
        "section_title": "Markets & Buyer Committee Map",
        "title": "LinkedIn, events, chambers and research",
        "description": "Leverage ADIPEC, Big 5, trade chambers, Swapcard directories, and professional networks for evidence-driven sales intelligence.",
        "target_section": "events",
        "topics": [
            "Exhibition Lead Generation: ADIPEC Abu Dhabi, Saudi Build Riyadh, Big 5 Dubai, and Intermodal Europe",
            "Digital Intelligence & Swapcard: Pre-event exhibitor directory mining, Booth executive mapping, and booked meetings",
            "Bilateral Trade Bodies: Abu Dhabi Chamber, Dubai Chambers, Saudi Chambers, and European export trade missions",
            "Professional Association Networks: SPE (Petroleum), AMPP (Corrosion & Coatings), and SFPE (Fire Protection)"
        ]
    },

    # SECTION 4: Workflows & AI Prompts (Lessons 10 to 11)
    {
        "day_number": 10,
        "step_number": 10,
        "section_number": 4,
        "section_title": "Workflows & AI Prompts",
        "title": "AI research and evidence checking",
        "description": "Utilize structured B2B sales prompts for verified market research, decision-maker validation, and respectful personalized outreach drafting.",
        "target_section": "outreach",
        "topics": [
            "Evidence-First B2B Prompt: Structured prompting for company intelligence, revenue signals, and verified decision-makers",
            "Anti-Hallucination Guardrails: Cross-referencing AI outputs against official company registers and verified sources",
            "Personalized 120-Word Outreach Prompt: Crafting respectful, concise emails with specific value hooks and clear call-to-action",
            "Meeting Prep Briefing Prompt: Generating customized 5-question discovery agendas and anticipated objection responses"
        ]
    },
    {
        "day_number": 11,
        "step_number": 11,
        "section_number": 4,
        "section_title": "Workflows & AI Prompts",
        "title": "20-minute inbound: call, email, CRM",
        "description": "Master the 20-minute first-response SLA for inbound leads, multi-channel discovery calls, and strict CRM documentation protocols.",
        "target_section": "automation",
        "topics": [
            "Speed-to-Lead Cadence: The mandatory 20-minute first-response SLA for web and inbound RFQs",
            "Multi-Channel Triage: Phone call first for urgency, immediate follow-up email recap with agreed bullet points",
            "8-Stage Deal Pipeline: Market Signal → Verify ICP → Contact & Score → Call/Email → Meeting → Proposal → PO → Handover",
            "CRM Data Hygiene: Every interaction logged with owner, deadline, agreed next action, and client preferences"
        ]
    },

    # SECTION 5: Real Sales Case Studies (Lessons 12 to 14)
    {
        "day_number": 12,
        "step_number": 12,
        "section_number": 5,
        "section_title": "Real Sales Case Studies",
        "title": "Role-play: discovery, politeness and objections",
        "description": "Simulate high-stakes discovery conversations, polite qualification, objection handling, and client preference alignment.",
        "target_section": "outreach",
        "topics": [
            "Live Role-Play Simulation: Handling aggressive procurement directors demanding unrealistic approval guarantees",
            "Ambiguous Checklist Case: Resolving OEM confusion when multiple conflicting registration forms exist",
            "Proof Before Meeting Case: Supplying verified capability credentials and tentative buyer maps to overseas OEMs",
            "Objection Reframing: Moving conversations from price discounts to total risk mitigation and compliance guarantees"
        ]
    },
    {
        "day_number": 13,
        "step_number": 13,
        "section_number": 5,
        "section_title": "Real Sales Case Studies",
        "title": "Proposal, pricing, payment and risk gate",
        "description": "Structure compliant proposals, define payment milestones, avoid margin erosion, and conduct proposal QA before manager sign-off.",
        "target_section": "automation",
        "topics": [
            "PO Acknowledgment vs. Readiness Case: Why a signed PO is not project execution readiness until operational review",
            "Cash-Flow Pressure Case: Managing early payment requests and matching labor/material commitments to cash collections",
            "Proposal QA Gate: Checking exclusions, BOQ scope boundaries, Civil Defence approvals, and profit margin baseline",
            "Manager Sign-Off Protocols: Commercial sign-off matrix for contracts above standard authority limits"
        ]
    },
    {
        "day_number": 14,
        "step_number": 14,
        "section_number": 5,
        "section_title": "Real Sales Case Studies",
        "title": "Contract handover, client care and cross-selling",
        "description": "Execute seamless post-sale handover to technical operations, establish client retention checkpoints, and identify compliant cross-selling opportunities.",
        "target_section": "crosssell",
        "topics": [
            "Sales-to-Operations Handover: Delivering full client brief, approved drawings, BOQ, and payment milestones to project teams",
            "Dual-Entity Cross-Selling Playbook: When Plus UAE corporate clients legitimately require Vortexen PFP services",
            "Vortexen Contractor Referrals: Identifying when MEP contractors need Plus UAE business licensing, PRO, or CICPA passes",
            "Ethical Referral Boundaries: Cross-selling only when verified client need exists and capability is certified"
        ]
    },

    # SECTION 6: CRM Discipline & Funnel Simulator (Lesson 15 + Final Certification)
    {
        "day_number": 15,
        "step_number": 15,
        "section_number": 6,
        "section_title": "CRM Discipline & Funnel Simulator",
        "title": "CRM Discipline, Funnel Simulator & Final Certification Exam",
        "description": "Operate the interactive conversion funnel simulator, execute 0-100 prospect scoring, and complete the comprehensive graduation certification exam.",
        "target_section": "cases",
        "topics": [
            "Conversion Funnel Simulator: Interactive modeling of Outreach → Replies → Meetings → Proposals → Won Deals",
            "Prospect Scoring Practice: Real-time scoring of GCC enterprise leads using the 6-factor assessment matrix",
            "20-Minute SLA Response Simulator: Practicing rapid response protocols under live countdown simulation",
            "Final Knowledge Assessment: Comprehensive 10-Question Certification Exam requiring 80% passing grade to graduate"
        ]
    }
]
