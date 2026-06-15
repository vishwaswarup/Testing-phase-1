"""
Casualty Extractor
==================

Extracts killed and injured counts from text using regex patterns.

Handles patterns like:
    "269 people were killed"
    "500 were injured"
    "at least 30 dead"
    "more than 100 wounded"
    "killing 45 and injuring 200"
    "left 10 dead and 50 hurt"
"""

import re


# ---------------------------------------------------------------------------
# Regex patterns for KILLED
# ---------------------------------------------------------------------------
# Each pattern captures the number as group 1.
# We use word boundaries and case-insensitive matching.
KILLED_PATTERNS = [
    # "N people were killed" / "N soldiers were killed" / "N killed"
    r"(\d+)\s+(?:\w+\s+)?(?:were\s+)?killed",
    # "killed N people" / "killed N"
    r"killed\s+(\d+)(?:\s+people)?",
    # "killing N people" / "killing N"
    r"killing\s+(\d+)(?:\s+people)?",
    # "N dead" / "N people dead"
    r"(\d+)\s+(?:people\s+)?dead",
    # "N fatalities"
    r"(\d+)\s+fatalities",
    # "N deaths"
    r"(\d+)\s+deaths",
    # "left N dead"
    r"left\s+(\d+)\s+dead",
    # "claimed N lives" / "claimed the lives of N"
    r"claimed\s+(?:the\s+lives\s+of\s+)?(\d+)\s+lives?",
    r"claimed\s+(\d+)\s+lives",
    # "N casualties" (often means killed, but can be ambiguous)
    r"(\d+)\s+(?:were\s+)?(?:confirmed\s+)?casualties",
    # "death toll of N" / "death toll rose to N"
    r"death\s+toll\s+(?:of|rose\s+to|reached|stands\s+at)\s+(\d+)",
    # "at least N died"
    r"(\d+)\s+(?:people\s+)?died",
]

# ---------------------------------------------------------------------------
# Regex patterns for INJURED
# ---------------------------------------------------------------------------
INJURED_PATTERNS = [
    # "N people were injured" / "N were injured" / "N injured"
    r"(\d+)\s+(?:people\s+)?(?:were\s+)?injured",
    # "injuring N" / "injured N"
    r"injuring\s+(\d+)(?:\s+\w+)?",
    r"injured\s+(\d+)(?:\s+\w+)?",
    # "injured more than N" / "injured at least N others"
    r"injured\s+(?:more\s+than|at\s+least|over|approximately|around|nearly|about)\s+(\d+)",
    # "N wounded"
    r"(\d+)\s+(?:people\s+)?(?:were\s+)?wounded",
    # "wounding N"
    r"wounding\s+(\d+)(?:\s+people)?",
    # "N hurt"
    r"(\d+)\s+(?:people\s+)?(?:were\s+)?hurt",
    # "left N injured/wounded/hurt"
    r"left\s+(\d+)\s+(?:injured|wounded|hurt)",
    # "N hospitalized" / "N people were hospitalized"
    r"(\d+)\s+(?:\w+\s+)?(?:were\s+)?hospitali[sz]ed",
]

# ---------------------------------------------------------------------------
# Prefix pattern — handles "at least", "more than", "approximately", etc.
# These appear before the number and should be stripped.
# ---------------------------------------------------------------------------
PREFIX = r"(?:at\s+least|more\s+than|over|approximately|around|nearly|about|up\s+to)?\s*"


def _find_max_number(text: str, patterns: list[str]) -> int:
    """
    Search text for all matching patterns and return the largest
    number found.  Returns 0 if no match.

    We take the max because multiple patterns may match different
    mentions, and the highest is usually the most recent/final count.
    """
    numbers = []
    for pattern in patterns:
        # Prepend the optional prefix to every pattern
        full_pattern = PREFIX + pattern
        for match in re.finditer(full_pattern, text, re.IGNORECASE):
            try:
                numbers.append(int(match.group(1)))
            except (IndexError, ValueError):
                continue
    return max(numbers) if numbers else 0


def extract_casualties(text: str) -> dict:
    """
    Extract killed and injured counts from text.

    Parameters
    ----------
    text : str
        The raw text to search.

    Returns
    -------
    dict with keys:
        killed  – number of people killed (int, 0 if unknown)
        injured – number of people injured (int, 0 if unknown)
    """
    return {
        "killed": _find_max_number(text, KILLED_PATTERNS),
        "injured": _find_max_number(text, INJURED_PATTERNS),
    }


# ---------------------------------------------------------------------------
# Standalone test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    samples = [
        "A bomb exploded killing 45 people and injuring 200.",
        "The attack left 30 dead and 150 wounded.",
        "At least 269 people were killed and more than 500 were injured.",
        "The death toll rose to 12. Over 50 people were hospitalized.",
        "No casualties were reported in the incident.",
    ]

    for s in samples:
        result = extract_casualties(s)
        print(f"Text: {s}")
        print(f"  Killed : {result['killed']}")
        print(f"  Injured: {result['injured']}")
        print()
