"""
Location Extractor
==================

Extracts country, state, and city from text using a hybrid approach:
    1. spaCy NER for candidate GPE (geopolitical entity) entities.
    2. Region configuration lookup for validation.
    3. Country-city mapping for disambiguation.

Returns a confidence score based on extraction quality.
"""

import os
import sys
import spacy

# Ensure project root is on the path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.regions import ACTIVE_COUNTRIES, CITY_TO_COUNTRY_MAP, COUNTRY_SET_LOWER

# ---------------------------------------------------------------------------
# Load spaCy model
# ---------------------------------------------------------------------------
nlp = spacy.load("en_core_web_sm")


def extract_location(text: str) -> dict:
    """
    Extract country, state, city, and a confidence score from text.

    Parameters
    ----------
    text : str
        The raw text to analyse.

    Returns
    -------
    dict with keys:
        country    – the country name (str, "" if not found)
        state      – the state/province name (str, "" if not found)
        city       – the city name (str, "" if not found)
        confidence – extraction confidence score (float, 0.0 to 1.0)
    """

    doc = nlp(text)

    # Collect all GPE entities (deduplicated, preserving order)
    gpes = []
    seen = set()
    for ent in doc.ents:
        if ent.label_ == "GPE" and ent.text not in seen:
            gpes.append(ent.text)
            seen.add(ent.text)

    country = ""
    state = ""
    city = ""
    confidence = 0.0

    non_country_gpes = []
    
    # 1. Check for explicit countries
    for gpe in gpes:
        if gpe.lower() in COUNTRY_SET_LOWER:
            if not country:
                # Find the properly capitalized version
                for active_country in ACTIVE_COUNTRIES:
                    if active_country.lower() == gpe.lower():
                        country = active_country
                        break
        else:
            non_country_gpes.append(gpe)

    # 2. Check for cities in our region config
    found_known_city = False
    for gpe in non_country_gpes:
        if gpe.lower() in CITY_TO_COUNTRY_MAP:
            city = gpe
            mapped_country = CITY_TO_COUNTRY_MAP[gpe.lower()]
            if not country:
                country = mapped_country  # Infer country from known city
            found_known_city = True
            break
            
    # 3. Heuristic: if no known city found, use the first non-country GPE as city.
    if not city and len(non_country_gpes) >= 1:
        city = non_country_gpes[0]
        
    # State is the next available non-country GPE
    state_candidates = [g for g in non_country_gpes if g != city]
    if len(state_candidates) >= 1:
        state = state_candidates[0]

    # 4. Calculate confidence
    if country and found_known_city:
        confidence = 1.0  # High confidence: we know this city is in this country
    elif country and city:
        confidence = 0.8  # Found country and some unknown city
    elif country:
        confidence = 0.7  # Found country only
    elif city:
        confidence = 0.5  # Found unknown city only
    else:
        confidence = 0.0  # Found nothing

    return {
        "country": country,
        "state": state,
        "city": city,
        "confidence": confidence
    }


# ---------------------------------------------------------------------------
# Standalone test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    samples = [
        "A bombing attack occurred in Colombo on April 21, 2019.",
        "The attack took place in Mumbai, Maharashtra.",
        "An explosion was reported near Kabul, Afghanistan.",
        "The incident occurred in Paris, France.",
        "A terrorist attack in Pulwama, Jammu and Kashmir.",
        "No location information available."
    ]

    for s in samples:
        result = extract_location(s)
        print(f"Text: {s}")
        print(f"  Country   : {result['country']!r}")
        print(f"  State     : {result['state']!r}")
        print(f"  City      : {result['city']!r}")
        print(f"  Confidence: {result['confidence']}")
        print()
