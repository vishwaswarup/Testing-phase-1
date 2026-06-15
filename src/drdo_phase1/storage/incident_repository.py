"""
Phase 1C: Enhanced Incident Repository
========================================

Provides CRUD operations for incidents and documents in SQLite.

Key improvements over the original:
- Uses JSON arrays for list fields (not comma-separated strings)
- INSERT OR REPLACE (upsert) to support dedup-merge updates
- Persists retrieval_text and all new Phase 1C fields
- Query helpers for filtering, searching, and statistics
- Document tracking via save_document()
"""

import json
import os
import sys
from datetime import datetime

# ---------------------------------------------------------------------------
# Ensure project root is on the path
# ---------------------------------------------------------------------------
_STORAGE_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_DIR = os.path.dirname(_STORAGE_DIR)
if _PROJECT_DIR not in sys.path:
    sys.path.insert(0, _PROJECT_DIR)

from storage.database import get_connection, initialize_database


# ---------------------------------------------------------------------------
# Incident Operations
# ---------------------------------------------------------------------------

def save_incident(incident):
    """
    Save (or update) an Incident object into SQLite.

    Uses INSERT OR REPLACE so that deduplication merges can
    overwrite existing records with the same incident_id.

    List fields are stored as JSON arrays for robust serialization.
    """
    # Auto-initialize the database tables on first use
    initialize_database()

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT OR REPLACE INTO incidents (
            incident_id,
            date,
            created_at,
            country,
            state,
            city,
            district,
            latitude,
            longitude,
            location_confidence,
            attack_types,
            target_types,
            weapon_types,
            severity,
            threat_category,
            responsible_groups,
            target_organizations,
            killed,
            injured,
            security_forces_killed,
            security_forces_injured,
            civilian_killed,
            civilian_injured,
            militant_killed,
            modus_operandi,
            response_actions,
            intelligence_source,
            summary,
            retrieval_text,
            source_document_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            incident.incident_id,
            incident.date,
            incident.created_at or datetime.now().isoformat(),
            incident.country,
            incident.state,
            incident.city,
            incident.district,
            incident.latitude,
            incident.longitude,
            incident.location_confidence,

            # Store lists as JSON arrays
            json.dumps(incident.attack_types),
            json.dumps(incident.target_types),
            json.dumps(incident.weapon_types),

            incident.severity,
            incident.threat_category,

            json.dumps(incident.responsible_groups),
            json.dumps(incident.target_organizations),

            incident.killed,
            incident.injured,
            incident.security_forces_killed,
            incident.security_forces_injured,
            incident.civilian_killed,
            incident.civilian_injured,
            incident.militant_killed,

            incident.modus_operandi,
            json.dumps(incident.response_actions),
            incident.intelligence_source,

            incident.summary,
            incident.retrieval_text,

            incident.source_document_id,
        ))

        conn.commit()
        conn.close()

        print(f"  [SQLite] Saved incident: {incident.incident_id}")

    except Exception as e:
        print(f"  [SQLite] DATABASE ERROR: {e}")


def save_document(document):
    """
    Save a Document record to the documents table for tracking.

    Parameters
    ----------
    document : Document
        The ingested document object.
    """
    initialize_database()

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT OR REPLACE INTO documents (
            doc_id, source_type, source_path, title,
            language, page_count, char_count,
            ingested_at, metadata_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            document.doc_id,
            document.source_type,
            document.source_path,
            document.title,
            document.language,
            document.page_count,
            len(document.raw_text),
            datetime.now().isoformat(),
            json.dumps(document.metadata, default=str),
        ))

        conn.commit()
        conn.close()

    except Exception as e:
        print(f"  [SQLite] Document save error: {e}")


# ---------------------------------------------------------------------------
# Query: Basic Retrieval
# ---------------------------------------------------------------------------

def get_all_incidents():
    """Retrieve all incidents from the database."""
    initialize_database()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM incidents ORDER BY date DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_incident(incident_id):
    """Retrieve a single incident by its ID."""
    initialize_database()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM incidents WHERE incident_id = ?",
        (incident_id,)
    )
    row = cursor.fetchone()
    conn.close()
    return row


# ---------------------------------------------------------------------------
# Query: Filtered Retrieval
# ---------------------------------------------------------------------------

def get_incidents_by_country(country):
    """Get all incidents in a specific country."""
    initialize_database()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM incidents WHERE LOWER(country) = LOWER(?) ORDER BY date DESC",
        (country,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_incidents_by_state(state):
    """Get all incidents in a specific state/UT."""
    initialize_database()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM incidents WHERE LOWER(state) = LOWER(?) ORDER BY date DESC",
        (state,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_incidents_by_severity(severity):
    """Get all incidents of a specific severity level."""
    initialize_database()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM incidents WHERE UPPER(severity) = UPPER(?) ORDER BY date DESC",
        (severity,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_incidents_by_threat_category(category):
    """Get all incidents of a specific threat category."""
    initialize_database()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM incidents WHERE LOWER(threat_category) = LOWER(?) ORDER BY date DESC",
        (category,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_incidents_by_date_range(start_date, end_date):
    """
    Get incidents within a date range (inclusive).

    Parameters
    ----------
    start_date : str
        Start date in YYYY-MM-DD format.
    end_date : str
        End date in YYYY-MM-DD format.
    """
    initialize_database()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM incidents WHERE date >= ? AND date <= ? ORDER BY date DESC",
        (start_date, end_date)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def search_incidents(keyword):
    """
    Full-text search across summary and retrieval_text fields.

    Parameters
    ----------
    keyword : str
        Search term to look for.
    """
    initialize_database()
    conn = get_connection()
    cursor = conn.cursor()
    like_pattern = f"%{keyword}%"
    cursor.execute(
        """SELECT * FROM incidents
           WHERE summary LIKE ? OR retrieval_text LIKE ?
                 OR responsible_groups LIKE ? OR modus_operandi LIKE ?
           ORDER BY date DESC""",
        (like_pattern, like_pattern, like_pattern, like_pattern)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


# ---------------------------------------------------------------------------
# Query: Statistics & Analytics
# ---------------------------------------------------------------------------

def get_incident_statistics():
    """
    Get aggregate statistics from the incidents database.

    Returns
    -------
    dict
        Statistics including total counts, casualty sums,
        breakdowns by severity and threat category.
    """
    initialize_database()
    conn = get_connection()
    cursor = conn.cursor()

    stats = {}

    # Total counts
    cursor.execute("SELECT COUNT(*) as total FROM incidents")
    stats["total_incidents"] = cursor.fetchone()["total"]

    # Casualty totals
    cursor.execute("""
        SELECT
            COALESCE(SUM(killed), 0) as total_killed,
            COALESCE(SUM(injured), 0) as total_injured,
            COALESCE(SUM(security_forces_killed), 0) as total_sf_killed,
            COALESCE(SUM(security_forces_injured), 0) as total_sf_injured,
            COALESCE(SUM(civilian_killed), 0) as total_civ_killed,
            COALESCE(SUM(civilian_injured), 0) as total_civ_injured,
            COALESCE(SUM(militant_killed), 0) as total_militant_killed
        FROM incidents
    """)
    row = cursor.fetchone()
    stats["casualties"] = {
        "total_killed": row["total_killed"],
        "total_injured": row["total_injured"],
        "security_forces_killed": row["total_sf_killed"],
        "security_forces_injured": row["total_sf_injured"],
        "civilian_killed": row["total_civ_killed"],
        "civilian_injured": row["total_civ_injured"],
        "militant_killed": row["total_militant_killed"],
    }

    # By severity
    cursor.execute("""
        SELECT severity, COUNT(*) as count
        FROM incidents WHERE severity IS NOT NULL AND severity != ''
        GROUP BY severity ORDER BY count DESC
    """)
    stats["by_severity"] = {row["severity"]: row["count"] for row in cursor.fetchall()}

    # By threat category
    cursor.execute("""
        SELECT threat_category, COUNT(*) as count
        FROM incidents WHERE threat_category IS NOT NULL AND threat_category != ''
        GROUP BY threat_category ORDER BY count DESC
    """)
    stats["by_threat_category"] = {row["threat_category"]: row["count"] for row in cursor.fetchall()}

    # By country
    cursor.execute("""
        SELECT country, COUNT(*) as count
        FROM incidents WHERE country IS NOT NULL AND country != ''
        GROUP BY country ORDER BY count DESC
        LIMIT 10
    """)
    stats["by_country"] = {row["country"]: row["count"] for row in cursor.fetchall()}

    # By state (top 10)
    cursor.execute("""
        SELECT state, COUNT(*) as count
        FROM incidents WHERE state IS NOT NULL AND state != ''
        GROUP BY state ORDER BY count DESC
        LIMIT 10
    """)
    stats["by_state"] = {row["state"]: row["count"] for row in cursor.fetchall()}

    conn.close()
    return stats


def get_duplicate_candidates(date, country, state=None, city=None):
    """
    Find potential duplicate incidents for deduplication.

    Parameters
    ----------
    date : str
        Incident date in YYYY-MM-DD format.
    country : str
        Country name.
    state : str, optional
        State name for tighter matching.
    city : str, optional
        City name for tighter matching.

    Returns
    -------
    list
        List of matching incident rows.
    """
    initialize_database()
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM incidents WHERE date = ? AND LOWER(country) = LOWER(?)"
    params = [date, country]

    if state:
        query += " AND LOWER(state) = LOWER(?)"
        params.append(state)

    if city:
        query += " AND LOWER(city) = LOWER(?)"
        params.append(city)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows


def delete_incident(incident_id):
    """Delete an incident by its ID."""
    initialize_database()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM incidents WHERE incident_id = ?", (incident_id,))
    conn.commit()
    conn.close()