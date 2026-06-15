"""Incident data model for the DRDO Offline Multimodal Intelligence Analysis System.

This module defines the core :class:`Incident` dataclass used throughout the
pipeline to represent a single security incident extracted from unstructured
documents (text reports, images, audio transcripts, etc.).

Field reference
---------------

**Identity**

* ``incident_id``          – Unique identifier for the incident record.

**Location**

* ``date``                 – Date of the incident (ISO-8601 preferred, e.g. ``"2019-02-14"``).
* ``country``              – Country where the incident occurred.
* ``state``                – State / Union Territory (Indian context).
* ``city``                 – City or town name.
* ``district``             – Indian district (e.g. ``"Pulwama"``).
* ``latitude``             – Latitude of the incident location (decimal degrees).
* ``longitude``            – Longitude of the incident location (decimal degrees).
* ``location_confidence``  – Confidence score (0.0–1.0) for the geo-location.

**Attack profile**

* ``attack_types``         – List of attack type labels (e.g. ``["Suicide Bombing"]``).
* ``target_types``         – List of target type labels (e.g. ``["Military"]``).
* ``weapon_types``         – List of weapon/IED types used.
* ``responsible_groups``   – List of groups claiming or attributed responsibility.
* ``target_organizations`` – Specific organisations targeted.

**Casualties – aggregate**

* ``killed``               – Total persons killed.
* ``injured``              – Total persons injured.

**Casualties – disaggregated**

* ``security_forces_killed``  – Security-force personnel killed.
* ``security_forces_injured`` – Security-force personnel injured.
* ``civilian_killed``         – Civilians killed.
* ``civilian_injured``        – Civilians injured.
* ``militant_killed``         – Militants / insurgents neutralised.

**Classification**

* ``severity``             – Assessed severity: ``CRITICAL`` / ``HIGH`` / ``MEDIUM`` / ``LOW``.
* ``threat_category``      – Broad threat taxonomy label (e.g. ``"Terrorism"``,
                             ``"Insurgency"``, ``"Naxal/Maoist"``, ``"Cross-border"``).

**Operational details**

* ``modus_operandi``       – Free-text description of how the attack was carried out.
* ``response_actions``     – List of response actions taken (e.g. ``["Cordon"]``,
                             ``"Search Operation"``, ``"Encounter"``).
* ``intelligence_source``  – Primary intelligence channel: ``HUMINT`` / ``SIGINT`` /
                             ``OSINT`` / ``Media``.

**Narrative / retrieval**

* ``summary``              – Human-readable narrative summary of the incident.
* ``retrieval_text``       – Pre-built text blob optimised for vector-similarity search.
* ``source_document_id``   – Identifier of the originating document.

**Metadata**

* ``created_at``           – ISO-8601 timestamp of record creation.  Not set by
                             the dataclass default; the ingestion pipeline is
                             responsible for populating this field via
                             ``datetime.datetime.utcnow().isoformat()``.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field


@dataclass
class Incident:
    """Represents a single security incident with India-specific attributes.

    All list-typed fields use ``field(default_factory=list)`` to avoid the
    mutable-default pitfall.  ``created_at`` is left as an empty string by
    default; the pipeline should set it to an ISO-8601 timestamp at creation
    time (e.g. ``datetime.datetime.utcnow().isoformat()``).
    """

    # --- Identity -----------------------------------------------------------
    incident_id: str

    # --- Location -----------------------------------------------------------
    date: str = ""
    country: str = ""
    state: str = ""
    city: str = ""
    district: str = ""              # Indian district (e.g., "Pulwama")
    latitude: float = 0.0           # Latitude if mentioned
    longitude: float = 0.0          # Longitude if mentioned
    location_confidence: float = 0.0

    # --- Attack profile -----------------------------------------------------
    attack_types: list[str] = field(default_factory=list)
    target_types: list[str] = field(default_factory=list)
    weapon_types: list[str] = field(default_factory=list)
    responsible_groups: list[str] = field(default_factory=list)
    target_organizations: list[str] = field(default_factory=list)

    # --- Casualties (aggregate) ---------------------------------------------
    killed: int = 0
    injured: int = 0

    # --- Casualties (disaggregated) -----------------------------------------
    security_forces_killed: int = 0
    security_forces_injured: int = 0
    civilian_killed: int = 0
    civilian_injured: int = 0
    militant_killed: int = 0

    # --- Classification -----------------------------------------------------
    severity: str = ""              # CRITICAL / HIGH / MEDIUM / LOW
    threat_category: str = ""       # Terrorism, Insurgency, Naxal/Maoist, etc.

    # --- Operational details ------------------------------------------------
    modus_operandi: str = ""        # How the attack was carried out
    response_actions: list[str] = field(default_factory=list)
    intelligence_source: str = ""   # HUMINT / SIGINT / OSINT / Media

    # --- Narrative / retrieval ----------------------------------------------
    summary: str = ""
    retrieval_text: str = ""
    source_document_id: str = ""

    # --- Metadata -----------------------------------------------------------
    created_at: str = ""            # ISO timestamp – set by the pipeline


if __name__ == "__main__":
    # Quick demo: 2019 Pulwama attack
    pulwama = Incident(
        incident_id="INC-2019-0214-001",
        date="2019-02-14",
        country="India",
        state="Jammu & Kashmir",
        city="Pulwama",
        district="Pulwama",
        latitude=33.8742,
        longitude=75.1483,
        location_confidence=0.95,
        attack_types=["Suicide Bombing", "Vehicle-Borne IED"],
        target_types=["Military Convoy"],
        weapon_types=["Vehicle-Borne Improvised Explosive Device (VBIED)"],
        responsible_groups=["Jaish-e-Mohammed"],
        target_organizations=["Central Reserve Police Force (CRPF)"],
        killed=40,
        injured=35,
        security_forces_killed=40,
        security_forces_injured=35,
        civilian_killed=0,
        civilian_injured=0,
        militant_killed=1,
        severity="CRITICAL",
        threat_category="Terrorism",
        modus_operandi=(
            "A VBIED driven by a local militant rammed into a CRPF convoy "
            "of 78 vehicles on National Highway 44 near Lethpora, Pulwama."
        ),
        response_actions=["Cordon and Search Operation", "Encounter"],
        intelligence_source="OSINT",
        summary=(
            "On 14 February 2019, a Jaish-e-Mohammed suicide bomber rammed "
            "an explosive-laden vehicle into a CRPF convoy on NH-44 near "
            "Lethpora, Pulwama, killing 40 personnel and injuring 35. It "
            "remains one of the deadliest attacks on Indian security forces "
            "in Jammu & Kashmir."
        ),
        retrieval_text=(
            "Pulwama attack 2019 Jaish-e-Mohammed CRPF convoy suicide "
            "bombing VBIED Jammu Kashmir Lethpora NH44"
        ),
        source_document_id="DOC-OSINT-20190214-001",
        created_at=datetime.datetime.now(datetime.UTC).isoformat(),
    )

    print("=== Incident Record ===")
    print(f"  ID            : {pulwama.incident_id}")
    print(f"  Date          : {pulwama.date}")
    print(f"  Location      : {pulwama.city}, {pulwama.district}, {pulwama.state}")
    print(f"  Coordinates   : ({pulwama.latitude}, {pulwama.longitude})")
    print(f"  Confidence    : {pulwama.location_confidence}")
    print(f"  Attack Types  : {pulwama.attack_types}")
    print(f"  Weapon Types  : {pulwama.weapon_types}")
    print(f"  Responsible   : {pulwama.responsible_groups}")
    print(f"  Targets       : {pulwama.target_organizations}")
    print(f"  Killed (total): {pulwama.killed}")
    print(f"    SF killed   : {pulwama.security_forces_killed}")
    print(f"    Civ killed  : {pulwama.civilian_killed}")
    print(f"    Mil killed  : {pulwama.militant_killed}")
    print(f"  Injured       : {pulwama.injured}")
    print(f"  Severity      : {pulwama.severity}")
    print(f"  Threat Cat.   : {pulwama.threat_category}")
    print(f"  Modus Operandi: {pulwama.modus_operandi}")
    print(f"  Response      : {pulwama.response_actions}")
    print(f"  Intel Source  : {pulwama.intelligence_source}")
    print(f"  Summary       : {pulwama.summary[:80]}...")
    print(f"  Created At    : {pulwama.created_at}")
