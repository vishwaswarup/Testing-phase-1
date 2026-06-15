"""
Phase 1C: Enhanced Local LLM JSON Extractor
=============================================
Uses Ollama (llama3) to extract comprehensive, structured incident
fields from raw text, with a focus on Indian & South Asian security.

The schema is designed to capture extensive details about security
incidents including granular casualty breakdowns, threat classification,
modus operandi, and response actions.
"""
import json
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

# ---------------------------------------------------------------------------
# Comprehensive JSON Schema for Indian Security Incident Extraction
# ---------------------------------------------------------------------------
SCHEMA = {
    "type": "object",
    "properties": {
        "date": {
            "type": ["string", "null"],
            "description": "Date of the incident in YYYY-MM-DD format. null if unknown."
        },
        "country": {
            "type": ["string", "null"],
            "description": "Country where the incident occurred. null if unknown."
        },
        "state": {
            "type": ["string", "null"],
            "description": "State, province, or Union Territory. For India use official names like 'Jammu and Kashmir', 'Chhattisgarh', 'Manipur'. null if unknown."
        },
        "city": {
            "type": ["string", "null"],
            "description": "City, town, or locality. null if unknown."
        },
        "district": {
            "type": ["string", "null"],
            "description": "District name (especially for Indian incidents). null if unknown."
        },
        "coordinates": {
            "type": ["object", "null"],
            "properties": {
                "latitude": {"type": ["number", "null"]},
                "longitude": {"type": ["number", "null"]}
            },
            "description": "Latitude and longitude if explicitly mentioned. null if unknown."
        },
        "attack_types": {
            "type": ["array", "null"],
            "items": {"type": "string"},
            "description": "Categories of attack from: Bombing, IED Attack, Suicide Attack, Armed Assault, Ambush, Grenade Attack, Shelling, Kidnapping, Assassination, Hijacking, Arson, Stabbing, Vehicle Ramming, Drone Attack, Cyber Attack, VBIED. Multiple allowed."
        },
        "target_types": {
            "type": ["array", "null"],
            "items": {"type": "string"},
            "description": "Categories of target from: Military, Paramilitary, Police, Government, Religious, Civilian, Infrastructure, Media, Transportation, Diplomatic, Educational, Healthcare. Multiple allowed."
        },
        "weapon_types": {
            "type": ["array", "null"],
            "items": {"type": "string"},
            "description": "Weapons/methods used from: Explosives, IED, VBIED, Suicide Vest, Firearms, AK-47, Grenades, Rockets/RPG, Mortar, Landmine, Knife/Blade, Vehicle, Incendiary, Chemical, Drone/UAV. Multiple allowed."
        },
        "responsible_groups": {
            "type": ["array", "null"],
            "items": {"type": "string"},
            "description": "Named groups or organizations responsible. Use full names AND abbreviations if known, e.g., 'Jaish-e-Mohammed (JeM)'. Include 'Unknown' if perpetrator is unidentified. Common groups: Jaish-e-Mohammed, Lashkar-e-Taiba, Hizbul Mujahideen, CPI(Maoist), ULFA, NSCN, Islamic State, TRF."
        },
        "target_organizations": {
            "type": ["array", "null"],
            "items": {"type": "string"},
            "description": "Organizations/entities targeted. Common: CRPF, BSF, Indian Army, Rashtriya Rifles, J&K Police, Assam Rifles, ITBP, State Police, Civilians."
        },
        "casualties": {
            "type": ["object", "null"],
            "properties": {
                "killed": {
                    "type": ["integer", "null"],
                    "description": "Total people killed. null if unknown."
                },
                "injured": {
                    "type": ["integer", "null"],
                    "description": "Total people injured. null if unknown."
                },
                "security_forces_killed": {
                    "type": ["integer", "null"],
                    "description": "Security forces / military / police killed. null if unknown."
                },
                "security_forces_injured": {
                    "type": ["integer", "null"],
                    "description": "Security forces / military / police injured. null if unknown."
                },
                "civilian_killed": {
                    "type": ["integer", "null"],
                    "description": "Civilians killed. null if unknown."
                },
                "civilian_injured": {
                    "type": ["integer", "null"],
                    "description": "Civilians injured. null if unknown."
                },
                "militant_killed": {
                    "type": ["integer", "null"],
                    "description": "Militants / terrorists / insurgents killed. null if unknown."
                }
            }
        },
        "severity": {
            "type": ["string", "null"],
            "description": "Severity level: CRITICAL (mass casualty, 10+ killed or strategic target), HIGH (multiple casualties or significant target), MEDIUM (few casualties or minor target), LOW (no casualties, minor incident). null if cannot be determined."
        },
        "threat_category": {
            "type": ["string", "null"],
            "description": "Category from: Terrorism, Insurgency, Cross-Border Infiltration, Naxal/Maoist, Communal Violence, Cyber Attack, Maritime Security, Border Skirmish, Espionage, CBRN. null if unknown."
        },
        "modus_operandi": {
            "type": ["string", "null"],
            "description": "Detailed description of HOW the attack was carried out. Include vehicle type, approach method, timing, coordination etc. 2-3 sentences. null if unknown."
        },
        "response_actions": {
            "type": ["array", "null"],
            "items": {"type": "string"},
            "description": "Security response actions taken from: Cordon and Search, Encounter, Combing Operation, Area Domination, Aerial Surveillance, Surgical Strike, Artillery Response, Evacuation, Curfew Imposed, Internet Shutdown, Arrest, Case Registered. Multiple allowed."
        },
        "intelligence_source": {
            "type": ["string", "null"],
            "description": "Type of intelligence source: HUMINT, SIGINT, OSINT, Media Report, Official Statement, Press Release. null if unknown."
        },
        "summary": {
            "type": ["string", "null"],
            "description": "A detailed 3-5 sentence summary of the incident covering what happened, who was involved, where, when, and the aftermath."
        }
    },
    "required": [
        "date", "country", "state", "city", "district",
        "attack_types", "target_types", "weapon_types",
        "responsible_groups", "target_organizations",
        "casualties", "severity", "threat_category",
        "modus_operandi", "response_actions",
        "intelligence_source", "summary"
    ]
}


# ---------------------------------------------------------------------------
# India-focused Intelligence Analyst Prompt
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = (
    "You are a senior military intelligence analyst specializing in Indian "
    "and South Asian security affairs. You work for a defense research "
    "organization analyzing security incidents across India and its "
    "strategic neighborhood.\n\n"
    "Your expertise covers:\n"
    "- Counter-terrorism operations in Jammu & Kashmir\n"
    "- Northeast India insurgency (Manipur, Nagaland, Assam)\n"
    "- Naxal/Maoist left-wing extremism (Chhattisgarh, Jharkhand)\n"
    "- Cross-border infiltration and Pakistan-sponsored terrorism\n"
    "- India-China border tensions (LAC)\n"
    "- Maritime security threats\n\n"
    "Extract ALL security incident details from the following text into "
    "strict JSON format. Be thorough and precise:\n"
    "- Use official Indian state/UT names\n"
    "- Identify specific militant groups by full name AND abbreviation\n"
    "- Break down casualties by security forces, civilians, and militants\n"
    "- Classify severity based on scale and strategic impact\n"
    "- Detail the modus operandi\n"
    "- Note any security response actions mentioned\n\n"
    "CRITICAL ANTI-HALLUCINATION RULE:\n"
    "If the text does NOT describe a military, terrorism, or security incident "
    "(e.g., if it is an ordinary document, a cartoon, or a random image), "
    "do NOT invent or hallucinate an incident. Instead, provide a brief, accurate "
    "summary of what the text actually contains in the `summary` field, and "
    "leave ALL incident-specific fields (casualties, groups, weapons, etc.) "
    "as null or empty arrays.\n\n"
    "ONLY extract what is explicitly stated or can be directly inferred. "
    "If a field is unknown, use null.\n\n"
)


def extract_incident_json(raw_text: str, model: str = "llama3") -> dict:
    """
    Sends the raw text to the local Ollama LLM and extracts a comprehensive
    structured JSON response matching the Indian security incident schema.

    Parameters
    ----------
    raw_text : str
        The raw document text to analyze.
    model : str
        The Ollama model to use (default: llama3).

    Returns
    -------
    dict
        Extracted incident fields, or empty dict on failure.
    """
    prompt = SYSTEM_PROMPT + f"Text:\n{raw_text}\n"

    payload = {
        "model": model,
        "prompt": prompt,
        "format": SCHEMA,
        "stream": False,
        "options": {
            "temperature": 0.0,       # Deterministic extraction
            "num_predict": 4096,      # Allow longer responses for detailed extraction
        }
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=180)

        # Fallback: if schema formatting is not supported by the local Ollama
        # version, retry with generic format="json"
        if response.status_code == 400 and "format" in response.text.lower():
            payload["format"] = "json"
            payload["prompt"] += (
                "\nEnsure the output is ONLY valid JSON matching this schema: "
                + json.dumps(SCHEMA)
            )
            response = requests.post(OLLAMA_URL, json=payload, timeout=180)

        response.raise_for_status()
        result_text = response.json().get("response", "{}")
        return json.loads(result_text)

    except requests.exceptions.ConnectionError:
        print("[Error] Cannot connect to Ollama. Is it running on localhost:11434?")
        return {}
    except requests.exceptions.Timeout:
        print("[Warning] Ollama request timed out (180s). Try a smaller document.")
        return {}
    except json.JSONDecodeError as e:
        print(f"[Warning] LLM returned invalid JSON: {e}")
        return {}
    except Exception as e:
        print(f"[Warning] LLM Extraction failed: {e}")
        return {}


if __name__ == "__main__":
    # Test with a sample Indian security incident
    text = (
        "On February 14, 2019, a convoy of vehicles carrying Indian security "
        "personnel on the Jammu-Srinagar National Highway was attacked by a "
        "vehicle-borne improvised explosive device (VBIED) at Lethapora in the "
        "Pulwama district of Jammu and Kashmir. The attack resulted in the "
        "deaths of 40 Central Reserve Police Force (CRPF) personnel. The "
        "Pakistan-based militant group Jaish-e-Mohammed (JeM) claimed "
        "responsibility for the attack. The suicide bomber was identified as "
        "Adil Ahmad Dar, a local militant from Pulwama. In response, India "
        "launched surgical air strikes on a JeM training camp in Balakot, "
        "Pakistan on February 26, 2019."
    )
    print("Testing enhanced extraction...")
    result = extract_incident_json(text)
    print(json.dumps(result, indent=2))
