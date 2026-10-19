# Plus UAE × Vortexen AI Sales Academy

Production-grade full-stack learning management and certification platform for the **Plus UAE × Vortexen AI Sales Academy**, built with **FastAPI**, **SQLAlchemy 2.0**, **Alembic**, and **Vanilla Modern HTML/CSS/JS**.

---

## 1. System Architecture

```
PlusUae-Academic/
├── app/
│   ├── config.py              # Application settings & environment config
│   ├── database.py            # SQLAlchemy engine, session maker, get_db dependency
│   ├── security.py            # Argon2id password hashing, JWT tokens, RBAC dependencies
│   ├── assessment_data.py     # Authoritative 10-question bank & server-side answer key
│   ├── course_data.py         # Official tracks & 15-day sequential syllabus
│   ├── cli.py                 # Admin bootstrapping & course data seeding CLI
│   ├── main.py                # FastAPI app, CORS, routes, static asset mounts
│   ├── models/                # SQLAlchemy ORM database models
│   │   ├── user.py            # User & Invitation (expiring single-use tokens)
│   │   ├── course.py          # Course, CourseStep, Enrollment, StepProgress
│   │   ├── assessment.py      # ExamAttempt (authoritative attempt history)
│   │   ├── certificate.py     # Certificate (unique code, score, verification hash)
│   │   ├── service_lesson.py  # ServiceLesson (admin draft & published updates)
│   │   └── audit.py           # AuditLog (governance logging)
│   ├── schemas/               # Pydantic v2 validation models
│   └── routers/               # REST API endpoints
│       ├── auth.py            # /api/auth (Login, Logout, Me, Validate, Activate)
│       ├── admin.py           # /api/admin (Learners, Service Lessons, Audit Logs)
│       ├── learning.py        # /api/courses (My Courses, Steps, Sequential Completion)
│       ├── assessment.py      # /api/assessment (Questions, Server-side Grading)
│       └── certificates.py    # /api/certificates (Eligibility, Issue, Verify, PDF)
├── alembic/                   # Database migrations
│   ├── env.py
│   └── versions/              # Migration scripts
├── tests/                     # Automated pytest test suite
│   ├── conftest.py            # Test database fixture & client setup
│   ├── test_auth.py           # Authentication, invitations, roles, deactivation
│   ├── test_progression.py    # Sequential completion enforcement & anti-skip logic
│   ├── test_assessment.py     # Server grading (8 passes, 7 fails, key stripping)
│   ├── test_certificates.py   # Automatic issuance, idempotency, public verification, PDF
│   ├── test_frontend.py       # Static asset and frontend route tests
│   └── test_e2e_workflow.py   # Complete 13-step acceptance workflow end-to-end
├── index.html                 # Complete integrated frontend (dark theme preserved)
├── requirements.txt           # Python dependencies
├── .env.example               # Template environment configuration
├── pytest.ini                 # Pytest configuration
└── README.md                  # Comprehensive technical documentation
```

---

## 2. Key Features & Implementation Highlights

### Zero Public Registration & Secure Invitations
- Public registration is strictly disallowed. Only authenticated administrators can onboard learners.
- When an administrator creates a learner, a cryptographically secure, single-use invitation token (72-hour expiry) is generated.
- The learner redeems the link (`/?invite=<token>`) to establish their own password (Argon2id hashed) and activate their account.
- Once redeemed, invitations are immediately invalidated.

### Coursera-Style Sequential Progression
- Step 1 is unlocked by default. Steps 2 through 15 remain strictly locked until the preceding step has been completed and verified on the server.
- Out-of-order completions and client-side skipping attempts are rejected with `HTTP 400 Bad Request`.
- Each step links directly to relevant curriculum material (Plus UAE services, Vortexen passive fire protection, buyer mapping, CRM workflows, AI prompts, case studies).
- Progression is persistently stored in the backend database and survives logouts, device switches, and browser refreshes.

### Assessment Integrity & Server-Side Grading
- The assessment questions endpoint (`/api/assessment/questions`) serves the 10 questions and answer options with all correct indices and rationales stripped.
- Learners cannot submit the exam until all 15 course steps are completed.
- Submissions are evaluated against the authoritative backend answer key.
- 80% passing threshold (at least 8 of 10 correct) is strictly enforced.
- Complete attempt history is recorded in the database.

### Automatic Persistent Certificate Issuance
- Certificates are issued only when both server conditions are met:
  1. All 15 sequential steps are marked complete in the database.
  2. A qualifying exam attempt (score >= 80%) exists in the database.
- Certificates are unforgeable and use trusted database records for the learner's name and track.
- Generates a unique, non-guessable code (e.g. `PUVX-2026-XXXX-XXXX`).
- Repeated issuance requests are idempotent (never produces duplicate certificates).
- High-resolution printable PDF generation via ReportLab (`/api/certificates/{code}/pdf`).
- Public verification endpoint (`/api/certificates/verify/{code}`) allows external validation without authentication.

---

## 3. Local Setup & Startup Instructions

### Step 1: Create and Activate Virtual Environment
```powershell
# Create virtual environment with Python 3.12+
py -3.12 -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1
```

### Step 2: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 3: Configure Environment
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```
*(Default settings use SQLite `sales_academy.db` for local development, which requires zero external configuration).*

### Step 4: Run Alembic Database Migrations
```powershell
alembic upgrade head
```

### Step 5: Seed Course Data & Syllabus
```powershell
python -m app.cli seed-data
```

### Step 6: Bootstrap the Initial Administrator
Run the protected CLI command to create your first administrator:
```powershell
python -m app.cli create-admin --email admin@plusuae.com --name "Senior Sales Administrator"
```
*(You will be prompted to enter a secure password interactively, or you can supply `--password "YourSecretPass!"`).*

### Step 7: Launch the FastAPI Application
```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8001
```
Open your browser at **`http://127.0.0.1:8001/`** to access the application.
Interactive API documentation is available at **`http://127.0.0.1:8001/docs`**.

---

## 4. Administrator Workflow: Onboarding & Certification

### 1. Log in as Administrator
- Click **Sign In** in the top navigation bar.
- Enter the bootstrapped administrator credentials (`admin@plusuae.com`).
- The navigation updates with administrative controls.

### 2. Onboard a New Learner
- Open the **New services / Admin Portal** section.
- Select the **Learner Management** tab.
- Under **Create Learner Account**, enter:
  - Full Name: `Tariq Mansoor`
  - Email: `tariq@plusuae.com`
  - Assigned Course Track: `Plus UAE — Sales` (or `Both companies — Foundation` / `Vortexen — Technical Sales`)
- Click **Create Learner & Generate Invitation**.
- A single-use link is generated (e.g. `http://127.0.0.1:8001/?invite=TOKEN`). Click **Copy Invitation Link** and hand it securely to the learner.

### 3. Learner Activation & Progression
- The learner opens their invitation link.
- An activation dialog opens with their name and assigned course track pre-filled.
- The learner sets their password (minimum 8 characters) and clicks **Activate Account & Begin Training**.
- The learner is automatically logged in and taken to their assigned 15-day sequential learning plan.
- The learner reviews lessons and clicks **Mark Day Complete** for each day in order.

### 4. Taking the Final Exam & Earning Certificate
- After completing Day 15, the **Final Knowledge Test** unlocks.
- The learner answers the 10 questions and submits.
- Upon scoring 80% or higher, the learner is directed to the **Certificate** section.
- Click **Generate / View Official Certificate**.
- The learner can:
  - Print the certificate (`window.print()`).
  - Download a high-resolution PDF (`/api/certificates/{code}/pdf`).
  - Share the unique Certificate ID for online verification (`#verify={code}`).

### 5. Public Certificate Verification
- Anyone can verify an issued certificate by navigating to `#verify={code}` or opening the **Verify Authenticity** tool.
- The system confirms whether the certificate is authentic, issued to the registered learner, and for which course track.

---

## 5. Running Automated Tests

A comprehensive automated test suite covering authentication, RBAC, progression, server-side grading, certificates, and the full end-to-end acceptance workflow is included:

```powershell
# Run all tests
pytest -v

# Run specific test suites
pytest tests/test_auth.py -v
pytest tests/test_progression.py -v
pytest tests/test_assessment.py -v
pytest tests/test_certificates.py -v
pytest tests/test_e2e_workflow.py -v
```

All 16 tests execute and pass cleanly with SQLite test isolation.
