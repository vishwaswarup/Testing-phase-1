"""
Organization Extractor
======================

Extracts responsible groups (perpetrators) and target organisations (victims) from text.

Strategy:
    1. spaCy NER — find all ORG entities.
    2. Known groups lists — match against curated lists of
       known militant organisations and security forces.
    3. Context patterns — use linguistic indicators to classify
       groups as perpetrators or targets.
"""

import re
import spacy

# ---------------------------------------------------------------------------
# Load spaCy model
# ---------------------------------------------------------------------------
nlp = spacy.load("en_core_web_sm")

# ---------------------------------------------------------------------------
# Curated lists
# ---------------------------------------------------------------------------
KNOWN_MILITANT_GROUPS = [
    "Islamic State", "ISIS", "ISIL", "Daesh",
    "Al-Qaeda", "Al Qaeda", "al-Qa'ida",
    "Taliban",
    "Lashkar-e-Taiba", "LeT",
    "Jaish-e-Mohammed", "JeM",
    "Boko Haram",
    "Al-Shabaab", "al Shabaab",
    "Hamas",
    "Hezbollah", "Hizbullah",
    "Hizbul Mujahideen",
    "LTTE", "Tamil Tigers",
    "PKK",
    "ETA",
    "IRA", "Provisional IRA",
    "Tehrik-i-Taliban Pakistan", "TTP",
    "Houthi", "Ansar Allah",
    "Abu Sayyaf",
    "Jemaah Islamiyah",
    "AQAP", "Al-Qaeda in the Arabian Peninsula",
    "AQIM", "Al-Qaeda in the Islamic Maghreb",
    "National Thowheed Jamath", "NTJ",
    "Indian Mujahideen",
    "Naxalites", "Maoists",
]

KNOWN_SECURITY_FORCES = [
    "CRPF", "BSF", "ITBP", "CISF",
    "Indian Army", "Indian Navy", "Indian Air Force",
    "Jammu and Kashmir Police", "J&K Police", "Delhi Police",
    "NIA", "Police", "Army", "Navy", "Air Force",
    "Security Forces", "Armed Forces", "NDRF"
]

# ---------------------------------------------------------------------------
# Context patterns
# ---------------------------------------------------------------------------

# The capture group stops at common prepositions, punctuation, or end of text
_ORG_NAME = r"([A-Z][\w\-']+(?:\s+[\w\-']+){0,5}?)(?:\s+(?:in|on|near|at|from|during|who|which|that|and|or)\b|[,.\;]|\s*$)"

PERPETRATOR_PATTERNS = [
    r"([A-Z][\w\s\-']{2,40}?)\s+claimed\s+responsibility",
    r"responsibility\s+was\s+claimed\s+by\s+(?:the\s+)?" + _ORG_NAME,
    r"carried\s+out\s+by\s+(?:the\s+)?" + _ORG_NAME,
    r"perpetrated\s+by\s+(?:the\s+)?" + _ORG_NAME,
    r"attributed\s+to\s+(?:the\s+)?" + _ORG_NAME,
    r"([A-Z][\w\s\-']{2,40}?)\s+(?:has\s+)?taken\s+credit",
    r"linked\s+to\s+(?:the\s+)?" + _ORG_NAME,
    r"blamed\s+on\s+(?:the\s+)?" + _ORG_NAME,
    r"militants\s+from\s+(?:the\s+)?" + _ORG_NAME,
    r"terrorists\s+from\s+(?:the\s+)?" + _ORG_NAME,
    r"insurgents\s+from\s+(?:the\s+)?" + _ORG_NAME,
    r"attack\s+by\s+(?:the\s+)?" + _ORG_NAME,
    r"bombing\s+by\s+(?:the\s+)?" + _ORG_NAME,
]

TARGET_PATTERNS = [
    r"([A-Z][\w\s\-']{2,40}?)\s+personnel\s+were\s+(?:killed|injured|wounded)",
    r"convoy\s+of\s+(?:the\s+)?" + _ORG_NAME,
    r"([A-Z][\w\s\-']{2,40}?)\s+(?:soldiers|troops|police)",
    r"targeted\s+(?!by\b)(?:the\s+)?" + _ORG_NAME,
    r"attacked\s+(?!by\b)(?:the\s+)?" + _ORG_NAME,
    r"victims\s+included\s+(?:the\s+)?" + _ORG_NAME,
    r"against\s+(?:the\s+)?" + _ORG_NAME,
]

def extract_organizations(text: str) -> dict:
    """
    Extract responsible groups and target organisations from text.

    Parameters
    ----------
    text : str
        The raw text to analyse.

    Returns
    -------
    dict
        {"responsible_groups": [...], "target_organizations": [...]}
    """

    responsible = []
    targets = []
    
    seen_resp = set()
    seen_targ = set()

    def _add_resp(name: str) -> None:
        name = name.strip()
        if name.lower().startswith("the "):
            name = name[4:]
        if name.lower() in ["local", "some", "many", "armed", "suspected"]:
            return
        if name and name.lower() not in seen_resp:
            seen_resp.add(name.lower())
            responsible.append(name)

    def _add_targ(name: str) -> None:
        name = name.strip()
        if name.lower().startswith("the "):
            name = name[4:]
        if name.lower() in ["local", "some", "many", "armed", "suspected"]:
            return
        if name and name.lower() not in seen_targ:
            seen_targ.add(name.lower())
            targets.append(name)

    text_lower = text.lower()

    # --- 1. Known Lists (Explicit Matches) ---------------------------------
    for group in KNOWN_MILITANT_GROUPS:
        if len(group) <= 4:
            if re.search(r"\b" + re.escape(group) + r"\b", text):
                _add_resp(group)
        else:
            if group.lower() in text_lower:
                _add_resp(group)

    for force in KNOWN_SECURITY_FORCES:
        if len(force) <= 4:
            if re.search(r"\b" + re.escape(force) + r"\b", text):
                _add_targ(force)
        else:
            if force.lower() in text_lower:
                _add_targ(force)

    # --- 2. Context Patterns -----------------------------------------------
    for pattern in PERPETRATOR_PATTERNS:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            _add_resp(match.group(1))

    for pattern in TARGET_PATTERNS:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            _add_targ(match.group(1))

    # --- 3. spaCy NER (Fallback classification) ----------------------------
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "ORG":
            name = ent.text.strip()
            if name.lower().startswith("the "):
                name = name[4:]
            name_lower = name.lower()
            
            # If already explicitly classified via lists or patterns, skip
            if name_lower in seen_resp or name_lower in seen_targ:
                continue
                
            # If it overlaps with known security forces, it's a target
            is_security_force = any(
                (f.lower() in name_lower) or (name_lower in f.lower()) 
                for f in KNOWN_SECURITY_FORCES
            )
            
            # If it overlaps with known militant groups, it's responsible
            is_militant = any(
                (m.lower() in name_lower) or (name_lower in m.lower())
                for m in KNOWN_MILITANT_GROUPS
            )
            
            if is_security_force:
                _add_targ(name)
            elif is_militant:
                _add_resp(name)
            else:
                # Ambiguous ORG without context context. We'll default to 
                # responsible, but only if it doesn't look like generic gov/police.
                if any(word in name_lower for word in ["police", "army", "navy", "force", "ministry", "department", "govt"]):
                    _add_targ(name)
                else:
                    # Filter out obvious mistakes like "Local"
                    if len(name) > 5:
                        _add_resp(name)

    # --- 4. Substring Deduplication ----------------------------------------
    # We want to keep the most specific name from KNOWN lists, or the cleaner one.
    # A simple approach: if "A" is in "B", we keep "A" if "A" is in KNOWN lists, else "B".
    # Since doing that perfectly is hard, let's do a basic containment filter:
    def deduplicate(items, known_set):
        # Sort by length descending
        items = sorted(list(set(items)), key=len, reverse=True)
        final = []
        for item in items:
            item_lower = item.lower()
            # Check if this item is a substring of an already accepted (longer) item
            # BUT if this item is EXACTLY in the known_set, we prefer the known item!
            # So if we have "Indian Army" and "Army", we keep "Indian Army" and discard "Army"
            # If we have "Lashkar-e-Taiba operatives" and "Lashkar-e-Taiba", we want to keep "Lashkar-e-Taiba".
            # This means if an item contains a KNOWN item, the KNOWN item is better.
            
            # Let's check if the current item contains any KNOWN item
            contains_known = any(k.lower() in item_lower and k.lower() != item_lower for k in known_set)
            is_known = any(item_lower == k.lower() for k in known_set)
            
            if contains_known and not is_known:
                # This is a longer string that just wraps a known entity (e.g. "Lashkar-e-Taiba operatives")
                # We skip it because we will eventually process the known entity itself (which is shorter).
                continue
                
            # Otherwise, check if it's a substring of something we already accepted
            if any(item_lower in f.lower() for f in final):
                continue
                
            final.append(item)
        return final

    known_militants_set = set(KNOWN_MILITANT_GROUPS)
    known_forces_set = set(KNOWN_SECURITY_FORCES)

    responsible = deduplicate(responsible, known_militants_set)
    targets = deduplicate(targets, known_forces_set)

    return {
        "responsible_groups": responsible,
        "target_organizations": targets
    }


# ---------------------------------------------------------------------------
# Standalone test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    samples = [
        "Jaish-e-Mohammed claimed responsibility for the attack. 40 CRPF personnel were killed.",
        "ISIS claimed responsibility. Local police confirmed the casualties.",
        "The convoy of the Indian Army was targeted by Lashkar-e-Taiba militants."
    ]

    for s in samples:
        result = extract_organizations(s)
        print(f"Text: {s}")
        print(f"  Responsible: {result['responsible_groups']}")
        print(f"  Targets    : {result['target_organizations']}")
        print()
