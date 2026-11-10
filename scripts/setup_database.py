"""
Microstash Database Setup & Verification Script
Initializes or migrates SQLite database with full applicable schema, indices, and seed data.
"""

import sys
import os

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import get_connection, init_db
from app.config import settings

def main():
    print("=" * 65)
    print("  [*] Microstash Database Setup & Schema Verification")
    print("=" * 65)
    print(f"Target Database File: {settings.DB_PATH}")
    
    # 1. Run initialization & auto-migration
    init_db()
    print("[OK] Database tables and schema migrations verified.")

    # 2. Inspect tables and indices
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = [row["name"] for row in cursor.fetchall() if not row["name"].startswith("sqlite_")]
    print(f"\nActive Tables ({len(tables)}):")
    for t in tables:
        cursor.execute(f"SELECT COUNT(*) as cnt FROM {t}")
        cnt = cursor.fetchone()["cnt"]
        print(f"  - {t:<18} [{cnt} records]")

    cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND NOT name LIKE 'sqlite_%';")
    indices = [row["name"] for row in cursor.fetchall()]
    print(f"\nActive Indices ({len(indices)}):")
    for idx in indices:
        print(f"  - {idx}")

    print("\n[OK] Database setup complete! Schema is fully synced.")
    print("=" * 65)

if __name__ == "__main__":
    main()
