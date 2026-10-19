"""
Administrative Bootstrap Command Line Interface.
Provides secure, non-public administrator account creation.
"""

import sys
import argparse
import getpass
import os
from sqlalchemy.orm import Session

from app.database import SessionLocal, Base, engine
from app.models.user import User
from app.models.audit import AuditLog
from app.security import get_password_hash
from app.course_data import COURSE_TRACKS, FIFTEEN_DAY_SYLLABUS
from app.models.course import Course, CourseStep
from sqlalchemy import text

def ensure_schema_migrations(db: Session):
    """Safely migrate any missing columns in existing SQLite tables."""
    try:
        bind = db.get_bind()
        with bind.connect() as conn:
            res = conn.execute(text("PRAGMA table_info(course_steps)")).fetchall()
            if res:
                col_names = [r[1] for r in res]
                if "section_number" not in col_names:
                    conn.execute(text("ALTER TABLE course_steps ADD COLUMN section_number INTEGER DEFAULT 1"))
                if "section_title" not in col_names:
                    conn.execute(text("ALTER TABLE course_steps ADD COLUMN section_title VARCHAR(255)"))
                conn.commit()
    except Exception as e:
        pass

def seed_courses_if_needed(db: Session):
    """Seed the default course tracks and 15-day sequential steps if not present."""
    ensure_schema_migrations(db)
    for track in COURSE_TRACKS:
        c = db.query(Course).filter(Course.code == track["code"]).first()
        if not c:
            c = Course(
                code=track["code"],
                title=track["title"],
                track_name=track["track_name"],
                description=track["description"]
            )
            db.add(c)
            db.flush()

        # Check steps
        for step in FIFTEEN_DAY_SYLLABUS:
            s = db.query(CourseStep).filter(
                CourseStep.course_id == c.id,
                CourseStep.step_number == step["day_number"]
            ).first()
            if not s:
                s = CourseStep(
                    course_id=c.id,
                    step_number=step["day_number"],
                    day_number=step["day_number"],
                    section_number=step.get("section_number", 1),
                    section_title=step.get("section_title", "Plus UAE Service Catalog"),
                    title=step["title"],
                    description=step["description"],
                    target_section=step["target_section"],
                    is_mandatory=True
                )
                db.add(s)
            else:
                s.section_number = step.get("section_number", s.section_number or 1)
                s.section_title = step.get("section_title", s.section_title or "General")
                s.target_section = step.get("target_section", s.target_section)
    db.commit()
 
def seed_admin_if_needed(db: Session):
    """Ensure default administrator accounts exist (vital for serverless /tmp databases like Vercel)."""
    default_admins = [
        ("admin@plusuae.com", "System Administrator", os.environ.get("INITIAL_ADMIN_PASSWORD", "AdminSecurePass2026!")),
        ("mohanrajvmvm221023@gmail.com", "Mohan Raj", os.environ.get("INITIAL_ADMIN_PASSWORD", "AdminSecurePass2026!")),
        ("mohanrajrvrm221023@gmail.com", "Mohan Raj", os.environ.get("INITIAL_ADMIN_PASSWORD", "AdminSecurePass2026!")),
    ]
    env_admin_email = os.environ.get("BOOTSTRAP_ADMIN_EMAIL") or os.environ.get("INITIAL_ADMIN_EMAIL")
    env_admin_pass = os.environ.get("BOOTSTRAP_ADMIN_PASSWORD") or os.environ.get("INITIAL_ADMIN_PASSWORD")
    if env_admin_email and env_admin_pass:
        default_admins.append((env_admin_email, "Administrator", env_admin_pass))

    for email, name, pwd in default_admins:
        email_clean = email.lower().strip()
        user = db.query(User).filter(User.email == email_clean).first()
        if not user:
            admin = User(
                email=email_clean,
                full_name=name,
                hashed_password=get_password_hash(pwd),
                role="admin",
                is_active=True
            )
            db.add(admin)
            db.flush()
            audit = AuditLog(
                user_id=admin.id,
                action="AUTO_BOOTSTRAP_ADMIN",
                details=f"Admin account {email_clean} automatically bootstrapped"
            )
            db.add(audit)
    db.commit()

def create_admin(email: str, full_name: str, password: str = None):
    """Create or update an administrator account securely."""
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        seed_courses_if_needed(db)

        email_clean = email.lower().strip()
        existing = db.query(User).filter(User.email == email_clean).first()
        if existing:
            if existing.role == "admin":
                print(f"[!] Administrator with email {email_clean} already exists.")
                if password:
                    existing.hashed_password = get_password_hash(password)
                    db.commit()
                    print(f"[+] Password for existing administrator {email_clean} has been updated.")
                return
            else:
                existing.role = "admin"
                existing.is_active = True
                if password:
                    existing.hashed_password = get_password_hash(password)
                db.commit()
                print(f"[+] User {email_clean} promoted to Administrator.")
                return

        if not password:
            password = getpass.getpass("Enter administrator password (min 8 chars): ")
            confirm = getpass.getpass("Confirm password: ")
            if password != confirm:
                print("[-] Error: Passwords do not match.")
                sys.exit(1)

        if len(password) < 8:
            print("[-] Error: Password must be at least 8 characters long.")
            sys.exit(1)

        admin = User(
            email=email_clean,
            full_name=full_name.strip(),
            hashed_password=get_password_hash(password),
            role="admin",
            is_active=True
        )
        db.add(admin)
        db.flush()

        audit = AuditLog(
            user_id=admin.id,
            action="BOOTSTRAP_ADMIN",
            details=f"Administrator account {admin.email} bootstrapped via CLI"
        )
        db.add(audit)
        db.commit()
        print(f"[+] Administrator account '{email_clean}' successfully created.")
    finally:
        db.close()

def main():
    parser = argparse.ArgumentParser(description="Plus UAE × Vortexen Academy CLI")
    subparsers = parser.add_subparsers(dest="command")

    admin_parser = subparsers.add_parser("create-admin", help="Bootstrap an administrator account")
    admin_parser.add_argument("--email", required=True, help="Administrator email address")
    admin_parser.add_argument("--name", default="System Administrator", help="Full name of administrator")
    admin_parser.add_argument("--password", required=False, help="Password (or omit to enter interactively)")

    subparsers.add_parser("seed-data", help="Seed default course tracks and syllabus")

    args = parser.parse_args()

    if args.command == "create-admin":
        pwd = args.password or os.environ.get("INITIAL_ADMIN_PASSWORD")
        create_admin(args.email, args.name, pwd)
    elif args.command == "seed-data":
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        seed_courses_if_needed(db)
        db.close()
        print("[+] Course tracks and 15-day sequential syllabus seeded.")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
