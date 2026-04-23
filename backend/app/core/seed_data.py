"""
Seed script — Populate the database with realistic fake HCP data for demo/dev.

Usage:
    python -m app.core.seed_data          # normal seed (only if empty)
    python -m app.core.seed_data --force  # truncate + reseed
    python -m app.core.seed_data --reset  # DROP + recreate + seed (clean)
"""

import logging
import sys
from sqlalchemy import select, func, text

from app.core.database import SyncSessionLocal, Base
import app.models
from app.models.hcp import HCP, HCPSpecialty

logger = logging.getLogger(__name__)

SEED_HCPS = [
    {
        "id": 1,
        "full_name": "Dr. Priya Sharma",
        "specialty": HCPSpecialty.cardiologist,
        "institution": "Apollo Heart Center",
        "city": "Mumbai",
        "email": "priya.sharma@apollo.com",
        "phone": "+91-9876543210",
    },
    {
        "id": 2,
        "full_name": "Dr. Rajesh Mehta",
        "specialty": HCPSpecialty.oncologist,
        "institution": "Tata Memorial Hospital",
        "city": "Mumbai",
        "email": "r.mehta@tatamem.org",
        "phone": "+91-9123456789",
    },
    {
        "id": 3,
        "full_name": "Dr. Anita Desai",
        "specialty": HCPSpecialty.neurologist,
        "institution": "AIIMS Delhi",
        "city": "New Delhi",
        "email": "a.desai@aiims.edu",
        "phone": "+91-9988776655",
    },
    {
        "id": 4,
        "full_name": "Dr. Suresh Kumar",
        "specialty": HCPSpecialty.diabetologist,
        "institution": "Fortis Diabetes Clinic",
        "city": "Bengaluru",
        "email": "s.kumar@fortis.com",
        "phone": "+91-9871234560",
    },
    {
        "id": 5,
        "full_name": "Dr. Meera Nair",
        "specialty": HCPSpecialty.pulmonologist,
        "institution": "Narayana Health",
        "city": "Bengaluru",
        "email": "m.nair@narayana.com",
        "phone": "+91-9765432100",
    },
]

def reset_database():
    db = SyncSessionLocal()
    try:
        logger.warning("Dropping all tables...")

        # Drop all tables (CASCADE handles FKs)
        Base.metadata.drop_all(bind=db.bind)

        logger.warning("Recreating all tables...")
        Base.metadata.create_all(bind=db.bind)

        logger.info("Database reset complete.")

    except Exception as e:
        logger.error("Failed to reset database: %s", e)
        raise
    finally:
        db.close()

def seed_hcps(force: bool = False) -> None:
    db = SyncSessionLocal()

    try:
        if force:
            logger.warning("Force mode: truncating hcps table...")
            db.execute(text("TRUNCATE TABLE hcps RESTART IDENTITY CASCADE;"))
            db.commit()

        count = db.execute(select(func.count(HCP.id))).scalar() or 0

        if count > 0:
            logger.info("HCP table already has %d rows — skipping seed.", count)
            return

        for hcp_data in SEED_HCPS:
            db.add(HCP(**hcp_data))

        db.commit()
        logger.info("Seeded %d HCPs successfully.", len(SEED_HCPS))

    except Exception as e:
        db.rollback()
        logger.error("Seeding failed: %s", e)
        raise
    finally:
        db.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    force_flag = "--force" in sys.argv
    reset_flag = "--reset" in sys.argv

    if reset_flag:
        reset_database()
        seed_hcps(force=True)
    else:
        seed_hcps(force=force_flag)