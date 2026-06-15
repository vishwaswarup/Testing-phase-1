"""
Phase 1C: SQLite-Backed Deduplication Engine
==============================================

Checks for duplicate incidents using SQLite queries instead of
in-memory lists. Deduplication is based on date + country + state/city
matching, with intelligent merging of fields.

When a duplicate is found, the existing record is updated in-place
with the merged data using INSERT OR REPLACE.
"""

import os
import sys

# ---------------------------------------------------------------------------
# Ensure project root is on the path
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from models.incident import Incident
from storage.incident_repository import get_duplicate_candidates, save_incident


class IncidentDatabase:
    """
    SQLite-backed deduplication engine for incidents.

    Replaces the previous in-memory list approach with SQLite queries,
    ensuring that deduplication persists across pipeline runs.
    """

    def __init__(self):
        # Track merge count for reporting
        self.merge_count = 0
        self.new_count = 0

    def is_duplicate(self, inc1: Incident, inc2: Incident) -> bool:
        """
        Check if two incidents are likely the same event based on:
        - Date (must match exactly)
        - Country (case-insensitive match)
        - State (case-insensitive match, if both have values)
        """
        if not inc1.date or not inc2.date or inc1.date != inc2.date:
            return False

        if not inc1.country or not inc2.country:
            return False

        if inc1.country.lower() != inc2.country.lower():
            return False

        # If both have states, they must match too
        if inc1.state and inc2.state:
            if inc1.state.lower() != inc2.state.lower():
                return False

        return True

    def merge_incidents(self, existing: Incident, new: Incident) -> Incident:
        """
        Merge a new incident into an existing one.

        Strategy:
        - Keep the existing incident_id (it's the DB primary key)
        - Prefer non-empty string fields from either
        - Take max for numeric fields (casualties)
        - Union for list fields
        - Keep the longer summary
        - Combine source document IDs
        """
        merged = Incident(
            incident_id=existing.incident_id,

            # Temporal
            date=existing.date or new.date,
            created_at=existing.created_at or new.created_at,

            # Location — prefer existing, fill gaps from new
            country=existing.country or new.country,
            state=existing.state or new.state,
            city=existing.city or new.city,
            district=existing.district or new.district,
            latitude=existing.latitude if existing.latitude != 0.0 else new.latitude,
            longitude=existing.longitude if existing.longitude != 0.0 else new.longitude,
            location_confidence=max(existing.location_confidence, new.location_confidence),

            # Classification — union of lists
            attack_types=list(set(existing.attack_types + new.attack_types)),
            target_types=list(set(existing.target_types + new.target_types)),
            weapon_types=list(set(existing.weapon_types + new.weapon_types)),

            # Severity — take the higher severity
            severity=_higher_severity(existing.severity, new.severity),
            threat_category=existing.threat_category or new.threat_category,

            # Entities — union of lists
            responsible_groups=list(set(existing.responsible_groups + new.responsible_groups)),
            target_organizations=list(set(existing.target_organizations + new.target_organizations)),

            # Casualties — take max
            killed=max(existing.killed, new.killed),
            injured=max(existing.injured, new.injured),
            security_forces_killed=max(existing.security_forces_killed, new.security_forces_killed),
            security_forces_injured=max(existing.security_forces_injured, new.security_forces_injured),
            civilian_killed=max(existing.civilian_killed, new.civilian_killed),
            civilian_injured=max(existing.civilian_injured, new.civilian_injured),
            militant_killed=max(existing.militant_killed, new.militant_killed),

            # Operational details — prefer longer/non-empty
            modus_operandi=(
                existing.modus_operandi
                if len(existing.modus_operandi) >= len(new.modus_operandi)
                else new.modus_operandi
            ),
            response_actions=list(set(existing.response_actions + new.response_actions)),
            intelligence_source=existing.intelligence_source or new.intelligence_source,

            # Text — keep the longer version
            summary=(
                existing.summary
                if len(existing.summary) >= len(new.summary)
                else new.summary
            ),
            retrieval_text=existing.retrieval_text or new.retrieval_text,

            # Provenance — combine source docs
            source_document_id=_combine_source_ids(
                existing.source_document_id, new.source_document_id
            ),
        )
        return merged

    def add_incident(self, new_incident: Incident) -> Incident:
        """
        Add an incident, checking SQLite for duplicates first.

        If a duplicate is found, merges the new data into the existing
        record and updates it in the database.

        Returns the final (merged or new) Incident.
        """
        # Check for duplicates in SQLite
        if new_incident.date and new_incident.country:
            candidates = get_duplicate_candidates(
                date=new_incident.date,
                country=new_incident.country,
                state=new_incident.state or None,
            )

            if candidates:
                # Found a potential duplicate — merge with the first match
                existing_row = candidates[0]
                existing = _row_to_incident(existing_row)

                if self.is_duplicate(existing, new_incident):
                    merged = self.merge_incidents(existing, new_incident)
                    # Update the existing record in SQLite
                    save_incident(merged)
                    self.merge_count += 1
                    return merged

        # No duplicate — save as new
        save_incident(new_incident)
        self.new_count += 1
        return new_incident


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------

_SEVERITY_ORDER = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "": 0}


def _higher_severity(s1: str, s2: str) -> str:
    """Return the higher severity level."""
    rank1 = _SEVERITY_ORDER.get(s1.upper() if s1 else "", 0)
    rank2 = _SEVERITY_ORDER.get(s2.upper() if s2 else "", 0)
    if rank1 >= rank2:
        return s1 or s2
    return s2 or s1


def _combine_source_ids(id1: str, id2: str) -> str:
    """Combine two source document IDs, avoiding duplicates."""
    existing_ids = set(id1.split(",")) if id1 else set()
    new_ids = set(id2.split(",")) if id2 else set()
    combined = existing_ids | new_ids
    combined.discard("")
    return ",".join(sorted(combined))


def _row_to_incident(row) -> Incident:
    """
    Convert a SQLite Row object back into an Incident dataclass.
    Handles JSON-encoded list fields.
    """
    import json

    def _parse_list(val):
        """Parse a JSON array string or comma-separated string into a list."""
        if not val:
            return []
        try:
            parsed = json.loads(val)
            if isinstance(parsed, list):
                return parsed
        except (json.JSONDecodeError, TypeError):
            pass
        # Fallback: comma-separated
        return [s.strip() for s in val.split(",") if s.strip()]

    return Incident(
        incident_id=row["incident_id"],
        date=row["date"] or "",
        created_at=row["created_at"] or "",
        country=row["country"] or "",
        state=row["state"] or "",
        city=row["city"] or "",
        district=row["district"] or "",
        latitude=row["latitude"] or 0.0,
        longitude=row["longitude"] or 0.0,
        location_confidence=row["location_confidence"] or 0.0,
        attack_types=_parse_list(row["attack_types"]),
        target_types=_parse_list(row["target_types"]),
        weapon_types=_parse_list(row["weapon_types"]),
        severity=row["severity"] or "",
        threat_category=row["threat_category"] or "",
        responsible_groups=_parse_list(row["responsible_groups"]),
        target_organizations=_parse_list(row["target_organizations"]),
        killed=row["killed"] or 0,
        injured=row["injured"] or 0,
        security_forces_killed=row["security_forces_killed"] or 0,
        security_forces_injured=row["security_forces_injured"] or 0,
        civilian_killed=row["civilian_killed"] or 0,
        civilian_injured=row["civilian_injured"] or 0,
        militant_killed=row["militant_killed"] or 0,
        modus_operandi=row["modus_operandi"] or "",
        response_actions=_parse_list(row["response_actions"]),
        intelligence_source=row["intelligence_source"] or "",
        summary=row["summary"] or "",
        retrieval_text=row["retrieval_text"] or "",
        source_document_id=row["source_document_id"] or "",
    )
