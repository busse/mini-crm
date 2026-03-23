"""Reset database.

Drops all tables, re-runs Alembic migrations, then seeds with demo data.
WARNING: This deletes all data!
"""
import subprocess
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database import Base, engine
# Import models to register them with Base.metadata
from app import models  # noqa: F401


def reset():
    """Drop all tables, run migrations, and seed."""
    print("Resetting database...")

    # Drop all tables
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    # Also drop alembic_version (not in Base.metadata)
    from sqlalchemy import text
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS alembic_version"))
        conn.commit()
    # Dispose connection pool to ensure fresh connections after migrations
    engine.dispose()
    print("Tables dropped.")

    # Run Alembic migrations
    print("Running Alembic migrations...")
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        cwd=project_root,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"Migration failed: {result.stderr}")
        sys.exit(1)

    print("Migrations complete.")

    # Run seed script as subprocess to avoid module caching issues
    print("Seeding database...")
    seed_result = subprocess.run(
        [sys.executable, "scripts/seed.py"],
        cwd=project_root,
        capture_output=True,
        text=True,
    )
    print(seed_result.stdout)
    if seed_result.returncode != 0:
        print(f"Seed failed: {seed_result.stderr}")
        sys.exit(1)

    print("Database reset complete!")


if __name__ == "__main__":
    reset()
