"""
Phase 1C: Enhanced Incident Extraction Pipeline
=================================================

Converts a Document object into a richly populated Incident object
by running the Ollama LLM extractor as the primary engine, with
rule-based extractors as validation/fallback.

Flow
----
    Document
        ↓
    LLM Extractor (Ollama — primary, comprehensive extraction)
        ↓
    Rule-Based Extractors (fallback for any fields LLM missed)
        ├── Date Extractor
        ├── Location Extractor
        ├── Casualty Extractor
        ├── Organization Extractor
        └── Attack/Weapon/Target Extractor
        ↓
    Field Merger (LLM priority, rule-based fills gaps)
        ↓
    Incident Builder
        ↓
    SQLite Storage (save_incident)
        ↓
    Deduplication Check
        ↓
    Final Incident

Usage
-----
    python3 incident_pipeline.py

Then enter a file path when prompted. The file is first ingested
(Phase 1), then the incident is extracted (Phase 1C).
"""

import os
import sys
import uuid
from datetime import datetime

# ---------------------------------------------------------------------------
# Ensure project root is on the path
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from models.document import Document
from models.incident import Incident

# Primary: LLM-based extraction
from extraction.llm_extractor import extract_incident_json

# Fallback: Rule-based extractors
from extraction.date_extractor import extract_date
from extraction.location_extractor import extract_location
from extraction.casualty_extractor import extract_casualties
from extraction.organization_extractor import extract_organizations
from extraction.attack_extractor import (
    extract_attack_types,
    extract_weapon_types,
    extract_target_types,
)

# Storage & Deduplication
from deduplication import IncidentDatabase
from storage.incident_repository import save_incident, save_document

# Ingestion pipeline
from pipeline import ingest


# ---------------------------------------------------------------------------
# Summary & Retrieval Text Generators
# ---------------------------------------------------------------------------

def _make_summary(text: str, max_sentences: int = 3) -> str:
    """
    Generate a simple summary from the first few sentences.
    No LLM — just sentence splitting.
    """
    sentences = []
    for part in text.split(". "):
        part = part.strip()
        if part:
            # Re-add the period if it was removed by the split
            if not part.endswith("."):
                part += "."
            sentences.append(part)
            if len(sentences) >= max_sentences:
                break
    return " ".join(sentences)


def _make_retrieval_text(incident: Incident) -> str:
    """
    Build a structured retrieval sentence from extracted fields.

    Example output:
        "CRITICAL Terrorism: IED Attack targeting Paramilitary in
         Pulwama, Jammu and Kashmir, India causing 40 security forces
         fatalities on 2019-02-14. Perpetrators: Jaish-e-Mohammed (JeM)."
    """
    parts = []

    # Severity + Category prefix
    prefix_parts = []
    if incident.severity:
        prefix_parts.append(incident.severity)
    if incident.threat_category:
        prefix_parts.append(incident.threat_category)
    if prefix_parts:
        parts.append(" ".join(prefix_parts) + ":")

    # Attack type
    if incident.attack_types:
        parts.append(", ".join(incident.attack_types) + " attack")
    else:
        parts.append("Incident")

    # Targets
    if incident.target_types:
        parts.append("targeting " + ", ".join(incident.target_types) + " sites")

    # Location (granular)
    location_parts = [
        p for p in [
            incident.city, incident.district,
            incident.state, incident.country
        ] if p
    ]
    if location_parts:
        parts.append("in " + ", ".join(location_parts))

    # Casualties (detailed)
    casualty_parts = []
    if incident.security_forces_killed:
        casualty_parts.append(f"{incident.security_forces_killed} security forces killed")
    if incident.civilian_killed:
        casualty_parts.append(f"{incident.civilian_killed} civilians killed")
    if incident.militant_killed:
        casualty_parts.append(f"{incident.militant_killed} militants killed")
    if not casualty_parts:
        # Fallback to totals
        if incident.killed:
            casualty_parts.append(f"{incident.killed} fatalities")
        if incident.injured:
            casualty_parts.append(f"{incident.injured} injured")
    if casualty_parts:
        parts.append("causing " + " and ".join(casualty_parts))

    # Date
    if incident.date:
        parts.append(f"on {incident.date}")

    # Perpetrators
    if incident.responsible_groups:
        parts.append("Perpetrators: " + ", ".join(incident.responsible_groups))

    return " ".join(parts) + "."


# ---------------------------------------------------------------------------
# Core Pipeline: Build Incident from Document
# ---------------------------------------------------------------------------

def build_incident(document: Document) -> Incident:
    """
    Extract an Incident from a Document using a hybrid approach:

    1. Run the Ollama LLM for comprehensive extraction (primary).
    2. Run rule-based extractors as fallback for any fields the LLM missed.
    3. Merge results with LLM taking priority.
    4. Save to SQLite.

    Parameters
    ----------
    document : Document
        The ingested document to extract from.

    Returns
    -------
    Incident
        The extracted incident with all available fields populated.
    """
    text = document.raw_text

    # --- Step 1: LLM Extraction (Primary) -----------------------------------
    print(f"  [Phase 1C] Running Ollama LLM extraction...")
    llm_data = extract_incident_json(text)

    # --- Step 2: Rule-Based Extraction (Fallback) ---------------------------
    print(f"  [Phase 1C] Running rule-based extractors as fallback...")
    rb_date = extract_date(text)
    rb_location = extract_location(text)
    rb_casualties = extract_casualties(text)
    rb_orgs = extract_organizations(text)
    rb_attack_types = extract_attack_types(text)
    rb_weapon_types = extract_weapon_types(text)
    rb_target_types = extract_target_types(text)

    # --- Step 3: Merge (LLM priority, rule-based fills gaps) ----------------

    # Casualties
    llm_cas = llm_data.get("casualties") or {}
    killed = llm_cas.get("killed") or rb_casualties.get("killed", 0) or 0
    injured = llm_cas.get("injured") or rb_casualties.get("injured", 0) or 0
    sf_killed = llm_cas.get("security_forces_killed") or 0
    sf_injured = llm_cas.get("security_forces_injured") or 0
    civ_killed = llm_cas.get("civilian_killed") or 0
    civ_injured = llm_cas.get("civilian_injured") or 0
    mil_killed = llm_cas.get("militant_killed") or 0

    # Date
    date = llm_data.get("date") or rb_date or ""

    # Location
    country = llm_data.get("country") or rb_location.get("country", "") or ""
    state = llm_data.get("state") or rb_location.get("state", "") or ""
    city = llm_data.get("city") or rb_location.get("city", "") or ""
    district = llm_data.get("district") or ""
    location_confidence = rb_location.get("confidence", 0.0)

    # Coordinates
    coords = llm_data.get("coordinates") or {}
    latitude = coords.get("latitude") or 0.0
    longitude = coords.get("longitude") or 0.0

    # Classification — merge LLM arrays with rule-based
    attack_types = list(set(
        (llm_data.get("attack_types") or []) + (rb_attack_types or [])
    ))
    weapon_types = list(set(
        (llm_data.get("weapon_types") or []) + (rb_weapon_types or [])
    ))
    target_types = list(set(
        (llm_data.get("target_types") or []) + (rb_target_types or [])
    ))

    # Entities — merge LLM with rule-based
    responsible_groups = list(set(
        (llm_data.get("responsible_groups") or []) +
        (rb_orgs.get("responsible_groups", []) or [])
    ))
    target_organizations = list(set(
        (llm_data.get("target_organizations") or []) +
        (rb_orgs.get("target_organizations", []) or [])
    ))

    # New Phase 1C fields (LLM only)
    severity = llm_data.get("severity") or ""
    threat_category = llm_data.get("threat_category") or ""
    modus_operandi = llm_data.get("modus_operandi") or ""
    response_actions = llm_data.get("response_actions") or []
    intelligence_source = llm_data.get("intelligence_source") or ""
    summary = llm_data.get("summary") or _make_summary(text)

    # --- Step 4: Build the Incident -----------------------------------------
    incident = Incident(
        incident_id=str(uuid.uuid4()),
        date=date,
        created_at=datetime.now().isoformat(),
        country=country,
        state=state,
        city=city,
        district=district,
        latitude=latitude,
        longitude=longitude,
        location_confidence=location_confidence,
        attack_types=attack_types,
        target_types=target_types,
        weapon_types=weapon_types,
        severity=severity,
        threat_category=threat_category,
        responsible_groups=responsible_groups,
        target_organizations=target_organizations,
        killed=killed,
        injured=injured,
        security_forces_killed=sf_killed,
        security_forces_injured=sf_injured,
        civilian_killed=civ_killed,
        civilian_injured=civ_injured,
        militant_killed=mil_killed,
        modus_operandi=modus_operandi,
        response_actions=response_actions,
        intelligence_source=intelligence_source,
        summary=summary,
        source_document_id=document.doc_id,
    )

    # Generate retrieval text from the extracted fields
    incident.retrieval_text = _make_retrieval_text(incident)

    return incident


# ---------------------------------------------------------------------------
# Pretty-Print an Incident
# ---------------------------------------------------------------------------

def print_incident(incident: Incident) -> None:
    """Print a formatted incident report with all Phase 1C fields."""

    print()
    print("=" * 70)
    print("  EXTRACTED INCIDENT — Phase 1C")
    print("=" * 70)
    print()
    print(f"  Incident ID         : {incident.incident_id}")
    print(f"  Source Document      : {incident.source_document_id}")
    print(f"  Created At           : {incident.created_at}")
    print()

    # --- Temporal ---
    print(f"  Date                 : {incident.date or '(not found)'}")
    print()

    # --- Location ---
    print("  --- Location ---")
    print(f"  Country              : {incident.country or '(not found)'}")
    print(f"  State                : {incident.state or '(not found)'}")
    print(f"  District             : {incident.district or '(not found)'}")
    print(f"  City                 : {incident.city or '(not found)'}")
    if incident.latitude or incident.longitude:
        print(f"  Coordinates          : ({incident.latitude}, {incident.longitude})")
    print(f"  Loc. Confidence      : {incident.location_confidence:.2f}")
    print()

    # --- Classification ---
    print("  --- Classification ---")
    print(f"  Severity             : {incident.severity or '(not assessed)'}")
    print(f"  Threat Category      : {incident.threat_category or '(not categorized)'}")
    print(f"  Attack Types         : {incident.attack_types or '(none detected)'}")
    print(f"  Weapon Types         : {incident.weapon_types or '(none detected)'}")
    print(f"  Target Types         : {incident.target_types or '(none detected)'}")
    print()

    # --- Entities ---
    print("  --- Entities ---")
    print(f"  Responsible Groups   : {incident.responsible_groups or '(none detected)'}")
    print(f"  Target Organizations : {incident.target_organizations or '(none detected)'}")
    print()

    # --- Casualties ---
    print("  --- Casualties ---")
    print(f"  Total Killed         : {incident.killed}")
    print(f"  Total Injured        : {incident.injured}")
    print(f"  Security Forces K/I  : {incident.security_forces_killed} / {incident.security_forces_injured}")
    print(f"  Civilians K/I        : {incident.civilian_killed} / {incident.civilian_injured}")
    print(f"  Militants Killed     : {incident.militant_killed}")
    print()

    # --- Operational ---
    print("  --- Operational Details ---")
    if incident.modus_operandi:
        print(f"  Modus Operandi       : {incident.modus_operandi[:300]}")
        if len(incident.modus_operandi) > 300:
            print(f"                         ... (truncated)")
    else:
        print(f"  Modus Operandi       : (not found)")
    print(f"  Response Actions     : {incident.response_actions or '(none recorded)'}")
    print(f"  Intelligence Source  : {incident.intelligence_source or '(unknown)'}")
    print()

    # --- Text ---
    print("  --- Summary ---")
    if incident.summary:
        print(f"  {incident.summary[:400]}")
        if len(incident.summary) > 400:
            print(f"  ... (truncated)")
    print()
    print(f"  Retrieval Text       : {incident.retrieval_text}")
    print()
    print("=" * 70)
    print()


# ---------------------------------------------------------------------------
# Main Entry Point
# ---------------------------------------------------------------------------

def main():
    print()
    print("=" * 70)
    print("  DRDO Phase 1C — Enhanced Incident Extraction Pipeline")
    print("  Ollama LLM + Rule-Based Extractors + SQLite Storage")
    print("=" * 70)
    print()

    db = IncidentDatabase()

    while True:
        file_path = input("  Enter file path (or 'exit' to stop): ").strip()
        if file_path.lower() == 'exit':
            break

        # --- Phase 1: Ingest the file ---------------------------------------
        print()
        print(f"  [Phase 1] Ingesting: {file_path}")
        document = ingest(file_path)

        if document is None:
            print("  ⚠  Ingestion failed.")
            continue

        print(f"  [Phase 1] Document created: {document.doc_id}")
        print(f"  [Phase 1] Characters: {len(document.raw_text)}")

        # Track the document in SQLite
        save_document(document)

        # --- Phase 1C: Extract incident -------------------------------------
        print()
        print(f"  [Phase 1C] Extracting incident with enhanced pipeline...")

        incident = build_incident(document)
        print_incident(incident)

        # --- Deduplication --------------------------------------------------
        print(f"  [Dedup] Running SQLite-backed deduplication...")
        final_incident = db.add_incident(incident)
        if final_incident.incident_id != incident.incident_id:
            print("  ✅ Duplicate detected! Merged with existing incident.")
        else:
            print("  ✅ New incident stored in SQLite.")

        print(f"  [Stats] New: {db.new_count} | Merged: {db.merge_count}")
        print()


if __name__ == "__main__":
    main()
