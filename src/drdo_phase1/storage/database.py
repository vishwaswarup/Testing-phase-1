"""
Phase 1C: Enhanced SQLite Database Layer
==========================================

Manages the SQLite database for storing security incidents with
comprehensive schema support for Indian security analysis.

Tables
------
    incidents   — Main table storing structured incident records
    documents   — Tracks source documents that were ingested

Indexes are created on frequently queried columns for fast lookups.
The database file is stored relative to the project root.
"""

import os
import sqlite3

# ---------------------------------------------------------------------------
# Database Configuration
# ---------------------------------------------------------------------------
# Store the DB file in the project's src/drdo_phase1/ directory
_DB_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_DIR = os.path.dirname(_DB_DIR)
DB_PATH = os.path.join(_PROJECT_DIR, "incidents.db")


def get_connection():
    """
    Get a connection to the SQLite database.
    Uses Row factory for dict-like access to columns.
    Enables WAL mode for better concurrent read performance.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def create_tables():
    """
    Create all tables and indexes if they don't exist.

    The incidents table has been expanded to include:
    - Granular location fields (district, coordinates)
    - Broken-down casualty counts (security forces, civilians, militants)
    - Threat classification (severity, threat_category)
    - Operational details (modus_operandi, response_actions)
    - Intelligence metadata
    - Timestamps
    """
    conn = get_connection()
    cursor = conn.cursor()

    # -----------------------------------------------------------------
    # Incidents Table — Main storage for extracted security incidents
    # -----------------------------------------------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS incidents (
        incident_id             TEXT PRIMARY KEY,

        -- Temporal
        date                    TEXT,
        created_at              TEXT,

        -- Location
        country                 TEXT,
        state                   TEXT,
        city                    TEXT,
        district                TEXT,
        latitude                REAL DEFAULT 0.0,
        longitude               REAL DEFAULT 0.0,
        location_confidence     REAL DEFAULT 0.0,

        -- Classification
        attack_types            TEXT,       -- JSON array
        target_types            TEXT,       -- JSON array
        weapon_types            TEXT,       -- JSON array
        severity                TEXT,       -- CRITICAL / HIGH / MEDIUM / LOW
        threat_category         TEXT,       -- Terrorism, Insurgency, etc.

        -- Entities
        responsible_groups      TEXT,       -- JSON array
        target_organizations    TEXT,       -- JSON array

        -- Casualties (total)
        killed                  INTEGER DEFAULT 0,
        injured                 INTEGER DEFAULT 0,

        -- Casualties (broken down)
        security_forces_killed  INTEGER DEFAULT 0,
        security_forces_injured INTEGER DEFAULT 0,
        civilian_killed         INTEGER DEFAULT 0,
        civilian_injured        INTEGER DEFAULT 0,
        militant_killed         INTEGER DEFAULT 0,

        -- Operational Details
        modus_operandi          TEXT,
        response_actions        TEXT,       -- JSON array
        intelligence_source     TEXT,

        -- Text fields
        summary                 TEXT,
        retrieval_text          TEXT,

        -- Provenance
        source_document_id      TEXT
    )
    """)

    # -----------------------------------------------------------------
    # Documents Table — Tracks ingested source documents
    # -----------------------------------------------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        doc_id          TEXT PRIMARY KEY,
        source_type     TEXT,
        source_path     TEXT,
        title           TEXT,
        language        TEXT,
        page_count      INTEGER DEFAULT 0,
        char_count      INTEGER DEFAULT 0,
        ingested_at     TEXT,
        metadata_json   TEXT        -- Full metadata as JSON
    )
    """)

    # -----------------------------------------------------------------
    # Indexes for fast querying
    # -----------------------------------------------------------------
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_incidents_date ON incidents(date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_incidents_country ON incidents(country)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_incidents_state ON incidents(state)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_incidents_city ON incidents(city)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_incidents_district ON incidents(district)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_incidents_severity ON incidents(severity)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_incidents_threat_cat ON incidents(threat_category)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_incidents_created ON incidents(created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_incidents_source_doc ON incidents(source_document_id)")

    conn.commit()
    conn.close()


def initialize_database():
    """
    Initialize the database — create all tables and indexes.
    Safe to call multiple times (uses IF NOT EXISTS).
    """
    create_tables()
    print(f"[Database] Initialized successfully at: {DB_PATH}")


def reset_database():
    """
    Drop all tables and recreate them.
    WARNING: This destroys all data!
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS incidents")
    cursor.execute("DROP TABLE IF EXISTS documents")
    conn.commit()
    conn.close()
    create_tables()
    print(f"[Database] Reset complete. All data cleared.")


if __name__ == "__main__":
    initialize_database()
