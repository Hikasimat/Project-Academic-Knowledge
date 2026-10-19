from app.main import app
from app.database import Base, engine, SessionLocal
from app.cli import seed_courses_if_needed, seed_admin_if_needed

# Auto-initialize SQLite schema and seed administrator credentials in Vercel's ephemeral /tmp
try:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_courses_if_needed(db)
        seed_admin_if_needed(db)
    finally:
        db.close()
except Exception:
    pass
