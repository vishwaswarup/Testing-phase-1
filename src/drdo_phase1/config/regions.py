"""
Regional Geographic Knowledge — Expanded India Security Intelligence Edition
==============================================================================

A configuration-driven layer for geographic data used by the DRDO Offline
Multimodal Intelligence Analysis System.  This module provides:

* Comprehensive coverage of all 28 Indian states and 8 Union Territories.
* Conflict-zone classifications (J&K, LAC, Northeast, Naxal belt, borders).
* Known militant / terror organisations relevant to the Indian subcontinent.
* Indian security-force names and abbreviations.
* Threat-category taxonomy and severity levels.
* Pre-built lookup maps for O(1) city → country and city → state resolution.

All lists are intentionally kept as *plain Python data structures* so they can
be imported with zero external dependencies.
"""

from typing import Dict, List, Set

# ============================================================================
# 1.  SOUTH ASIA COUNTRIES
# ============================================================================

SOUTH_ASIA_COUNTRIES: List[str] = [
    "India",
    "Pakistan",
    "China",
    "Bangladesh",
    "Sri Lanka",
    "Nepal",
    "Bhutan",
    "Myanmar",
    "Afghanistan",
    "Maldives",
]

# ============================================================================
# 2.  COUNTRY → CITIES  (massively expanded)
# ============================================================================
# India is organised into sub-sections for readability. The final list is the
# union of all regional sub-lists.
# ============================================================================

# ---- India: Jammu & Kashmir ------------------------------------------------
_INDIA_JK = [
    "Srinagar", "Jammu", "Pulwama", "Shopian", "Anantnag", "Baramulla",
    "Kupwara", "Sopore", "Handwara", "Bandipora", "Budgam", "Kulgam",
    "Rajouri", "Poonch", "Kathua", "Udhampur", "Doda", "Kishtwar", "Reasi",
]

# ---- India: Ladakh ---------------------------------------------------------
_INDIA_LADAKH = [
    "Leh", "Kargil",
]

# ---- India: Northeast -------------------------------------------------------
_INDIA_NORTHEAST = [
    # Manipur
    "Imphal", "Churachandpur", "Ukhrul", "Thoubal", "Tamenglong",
    # Nagaland
    "Kohima", "Dimapur", "Mokokchung", "Mon",
    # Mizoram
    "Aizawl", "Champhai", "Lunglei",
    # Meghalaya
    "Shillong", "Tura",
    # Arunachal Pradesh
    "Itanagar", "Tawang", "Bomdila", "Ziro", "Pasighat",
    # Tripura
    "Agartala", "Udaipur",
    # Sikkim
    "Gangtok", "Namchi",
    # Assam
    "Guwahati", "Dispur", "Dibrugarh", "Silchar", "Tezpur",
    "Jorhat", "Nagaon", "Tinsukia", "Bongaigaon",
]

# ---- India: Naxal Belt ------------------------------------------------------
_INDIA_NAXAL = [
    # Chhattisgarh
    "Raipur", "Jagdalpur", "Bastar", "Dantewada", "Sukma",
    "Bijapur", "Narayanpur", "Kanker", "Kondagaon",
    # Jharkhand
    "Ranchi", "Latehar", "Gumla", "Bokaro", "Jamshedpur",
    "Hazaribagh", "Palamu", "Chatra",
    # Maharashtra (Naxal-affected)
    "Gadchiroli", "Gondia",
    # Odisha (Naxal-affected)
    "Malkangiri", "Koraput", "Rayagada",
    # Andhra Pradesh / Telangana fringe
    "Bhadrachalam",
]

# ---- India: Major Metros & State Capitals ------------------------------------
_INDIA_METROS_CAPITALS = [
    # National Capital Territory
    "New Delhi", "Delhi",
    # Maharashtra
    "Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad", "Thane",
    # West Bengal
    "Kolkata", "Siliguri", "Asansol", "Durgapur",
    # Tamil Nadu
    "Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem",
    # Karnataka
    "Bengaluru", "Mysuru", "Hubballi", "Mangaluru", "Belagavi",
    # Telangana
    "Hyderabad", "Warangal", "Nizamabad", "Karimnagar",
    # Andhra Pradesh
    "Amaravati", "Visakhapatnam", "Vijayawada", "Tirupati", "Guntur", "Kurnool",
    # Gujarat
    "Gandhinagar", "Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar",
    # Rajasthan
    "Jaipur", "Jodhpur", "Udaipur", "Kota", "Ajmer", "Bikaner",
    "Jaisalmer", "Barmer",
    # Uttar Pradesh
    "Lucknow", "Varanasi", "Agra", "Kanpur", "Prayagraj", "Meerut",
    "Noida", "Ghaziabad", "Gorakhpur", "Mathura", "Aligarh", "Ayodhya",
    # Bihar
    "Patna", "Gaya", "Bhagalpur", "Muzaffarpur", "Darbhanga",
    # Madhya Pradesh
    "Bhopal", "Indore", "Gwalior", "Jabalpur", "Ujjain",
    # Punjab
    "Chandigarh", "Amritsar", "Ludhiana", "Jalandhar", "Patiala",
    "Pathankot", "Bathinda", "Fazilka",
    # Haryana
    "Gurugram", "Faridabad", "Karnal", "Panipat", "Ambala", "Hisar",
    # Uttarakhand
    "Dehradun", "Haridwar", "Rishikesh", "Nainital", "Haldwani",
    # Himachal Pradesh
    "Shimla", "Dharamshala", "Manali", "Kullu", "Mandi",
    # Kerala
    "Thiruvananthapuram", "Kochi", "Kozhikode", "Thrissur", "Kannur",
    # Goa
    "Panaji", "Margao", "Vasco da Gama",
    # Odisha
    "Bhubaneswar", "Cuttack", "Puri", "Rourkela", "Sambalpur",
]

# ---- India: Border Towns & Strategic Points ----------------------------------
_INDIA_BORDER = [
    "Wagah", "Uri", "Turtuk", "Demchok", "Pangong",
    "Nathu La", "Moreh",
    # Indo-China border (Arunachal / Sikkim)
    "Doklam", "Chumbi",
    # LAC flashpoints
    "Galwan", "Depsang", "Hot Springs", "Gogra",
]

# ---- India: Union Territory cities (Andaman, Dadra, Daman, Lakshadweep, Puducherry)
_INDIA_UT_CITIES = [
    "Port Blair",           # Andaman & Nicobar Islands
    "Silvassa",             # Dadra and Nagar Haveli and Daman and Diu
    "Daman", "Diu",
    "Kavaratti",            # Lakshadweep
    "Puducherry",           # Puducherry
]

# Combined India city list (de-duplicated, order preserved)
_ALL_INDIA_CITIES: List[str] = list(dict.fromkeys(
    _INDIA_JK
    + _INDIA_LADAKH
    + _INDIA_NORTHEAST
    + _INDIA_NAXAL
    + _INDIA_METROS_CAPITALS
    + _INDIA_BORDER
    + _INDIA_UT_CITIES
))

COUNTRY_TO_CITIES: Dict[str, List[str]] = {
    "India": _ALL_INDIA_CITIES,

    "Pakistan": [
        "Islamabad", "Rawalpindi", "Karachi", "Lahore", "Peshawar",
        "Quetta", "Multan", "Faisalabad", "Gujranwala", "Sialkot",
        "Abbottabad", "Muzaffarabad", "Mirpur",
        "Hyderabad", "Bahawalpur", "Sukkur", "Larkana", "Mardan",
        "Mingora", "Swat", "Waziristan", "Chitral", "Gilgit",
        "Skardu", "Gwadar", "Turbat", "Zhob", "Dera Ismail Khan",
        "Bannu", "Kohat", "Dera Ghazi Khan",
    ],

    "China": [
        "Beijing", "Shanghai", "Guangzhou", "Shenzhen", "Chengdu",
        "Wuhan", "Lhasa", "Urumqi", "Kashgar", "Hotan",
        "Shigatse", "Nyingchi", "Aksai Chin", "Yatung",
        "Kunming", "Nanning", "Chongqing", "Xi'an", "Lanzhou",
    ],

    "Bangladesh": [
        "Dhaka", "Chittagong", "Khulna", "Sylhet", "Rajshahi",
        "Cox's Bazar", "Rangpur", "Barisal", "Comilla", "Mymensingh",
        "Narayanganj", "Gazipur",
    ],

    "Sri Lanka": [
        "Colombo", "Sri Jayawardenepura Kotte", "Kandy", "Galle",
        "Jaffna", "Trincomalee", "Batticaloa", "Negombo",
        "Anuradhapura", "Polonnaruwa", "Matara", "Kilinochchi",
        "Mullaitivu", "Mannar", "Vavuniya",
    ],

    "Nepal": [
        "Kathmandu", "Pokhara", "Lalitpur", "Biratnagar", "Bharatpur",
        "Birgunj", "Dharan", "Butwal", "Janakpur", "Hetauda",
        "Nepalgunj",
    ],

    "Bhutan": [
        "Thimphu", "Phuntsholing", "Paro", "Punakha",
        "Samdrup Jongkhar", "Gelephu", "Trashigang",
    ],

    "Myanmar": [
        "Naypyidaw", "Yangon", "Mandalay", "Bago", "Sittwe",
        "Myitkyina", "Tamu", "Monywa", "Pathein", "Lashio",
        "Sagaing", "Mawlamyine",
    ],

    "Afghanistan": [
        "Kabul", "Kandahar", "Herat", "Mazar-i-Sharif", "Jalalabad",
        "Kunduz", "Ghazni", "Lashkar Gah", "Farah", "Taloqan",
        "Baghlan", "Pul-e-Khumri", "Khost", "Gardez",
    ],

    "Maldives": [
        "Male", "Addu City", "Fuvahmulah", "Kulhudhuffushi",
    ],
}

# ============================================================================
# 3.  INDIAN STATES & UNION TERRITORIES  →  Capitals
# ============================================================================
# 28 States + 8 Union Territories as of 2024.
# ============================================================================

INDIAN_STATES_AND_UTS: Dict[str, str] = {
    # ------ States (28) ------------------------------------------------------
    "Andhra Pradesh":            "Amaravati",
    "Arunachal Pradesh":         "Itanagar",
    "Assam":                     "Dispur",
    "Bihar":                     "Patna",
    "Chhattisgarh":              "Raipur",
    "Goa":                       "Panaji",
    "Gujarat":                   "Gandhinagar",
    "Haryana":                   "Chandigarh",
    "Himachal Pradesh":          "Shimla",
    "Jharkhand":                 "Ranchi",
    "Karnataka":                 "Bengaluru",
    "Kerala":                    "Thiruvananthapuram",
    "Madhya Pradesh":            "Bhopal",
    "Maharashtra":               "Mumbai",
    "Manipur":                   "Imphal",
    "Meghalaya":                 "Shillong",
    "Mizoram":                   "Aizawl",
    "Nagaland":                  "Kohima",
    "Odisha":                    "Bhubaneswar",
    "Punjab":                    "Chandigarh",
    "Rajasthan":                 "Jaipur",
    "Sikkim":                    "Gangtok",
    "Tamil Nadu":                "Chennai",
    "Telangana":                 "Hyderabad",
    "Tripura":                   "Agartala",
    "Uttar Pradesh":             "Lucknow",
    "Uttarakhand":               "Dehradun",
    "West Bengal":               "Kolkata",

    # ------ Union Territories (8) --------------------------------------------
    "Andaman and Nicobar Islands":              "Port Blair",
    "Chandigarh":                                "Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu":  "Daman",
    "Delhi":                                     "New Delhi",
    "Jammu and Kashmir":                         "Srinagar",
    "Ladakh":                                    "Leh",
    "Lakshadweep":                               "Kavaratti",
    "Puducherry":                                "Puducherry",
}

# ============================================================================
# 4.  CONFLICT ZONES
# ============================================================================
# Key areas of active or recent conflict, grouped by theatre.
# ============================================================================

CONFLICT_ZONES: Dict[str, List[str]] = {
    "jammu_kashmir": [
        "Pulwama", "Shopian", "Anantnag", "Baramulla", "Kupwara",
        "Sopore", "Handwara", "Bandipora", "Budgam", "Kulgam",
        "Rajouri", "Poonch",
    ],
    "ladakh_lac": [
        "Galwan", "Pangong", "Demchok", "Depsang", "Hot Springs", "Gogra",
    ],
    "northeast_insurgency": [
        "Imphal", "Churachandpur", "Ukhrul", "Kohima", "Dimapur",
        "Mon", "Mokokchung", "Itanagar", "Tinsukia",
    ],
    "naxal_belt": [
        "Dantewada", "Sukma", "Bijapur", "Narayanpur", "Bastar",
        "Latehar", "Gumla", "Gadchiroli", "Malkangiri", "Koraput",
    ],
    "indo_pak_border": [
        "Pathankot", "Uri", "Amritsar", "Wagah", "Fazilka",
        "Barmer", "Jaisalmer",
    ],
    "indo_china_border": [
        "Tawang", "Bomdila", "Nathu La", "Doklam", "Chumbi",
    ],
}

# ============================================================================
# 5.  KNOWN MILITANT / TERROR GROUPS
# ============================================================================

KNOWN_MILITANT_GROUPS: List[str] = [
    # ---- Kashmir-focused ----------------------------------------------------
    "Jaish-e-Mohammed", "JeM",
    "Lashkar-e-Taiba", "LeT",
    "Hizbul Mujahideen", "HM",
    "Al-Badr",
    "Harkat-ul-Mujahideen", "HuM",
    "Ansar Ghazwat-ul-Hind", "AGHUH",
    "The Resistance Front", "TRF",
    "Islamic State Jammu & Kashmir", "ISJK",

    # ---- Northeast India ----------------------------------------------------
    "ULFA", "United Liberation Front of Assam", "ULFA-I",
    "NSCN-IM", "NSCN-K", "National Socialist Council of Nagaland",
    "PLA", "People's Liberation Army", "PREPAK", "UNLF",
    "NDFB", "National Democratic Front of Bodoland",
    "KLO", "Kamtapur Liberation Organisation",
    "HNLC", "Hynniewtrep National Liberation Council",

    # ---- Naxal / Maoist -----------------------------------------------------
    "CPI(Maoist)", "CPI-Maoist", "Communist Party of India (Maoist)",
    "PLGA", "People's Liberation Guerrilla Army",
    "Naxalites", "Maoists", "Left Wing Extremists", "LWE",

    # ---- Pakistan-based / Transnational -------------------------------------
    "Tehrik-i-Taliban Pakistan", "TTP",
    "Al-Qaeda", "Al Qaeda",
    "Islamic State", "ISIS", "ISIL", "IS", "Daesh",
    "Indian Mujahideen", "IM", "SIMI",
    "Students Islamic Movement of India",

    # ---- Sri Lanka ----------------------------------------------------------
    "LTTE", "Liberation Tigers of Tamil Eelam",

    # ---- International / Other ----------------------------------------------
    "Taliban", "Boko Haram", "Al-Shabaab",
]

# ============================================================================
# 6.  INDIAN SECURITY FORCES
# ============================================================================

INDIAN_SECURITY_FORCES: List[str] = [
    # ---- Paramilitary / Central Armed Police Forces -------------------------
    "CRPF", "Central Reserve Police Force",
    "BSF", "Border Security Force",
    "ITBP", "Indo-Tibetan Border Police",
    "SSB", "Sashastra Seema Bal",
    "CISF", "Central Industrial Security Force",
    "NSG", "National Security Guard",
    "Assam Rifles", "AR",
    "RPF", "Railway Protection Force",

    # ---- Military -----------------------------------------------------------
    "Indian Army", "Indian Air Force", "IAF", "Indian Navy",
    "Rashtriya Rifles", "RR",
    "Para SF", "MARCOS", "Garud Commando Force",

    # ---- Intelligence & Investigation ---------------------------------------
    "RAW", "Research and Analysis Wing",
    "IB", "Intelligence Bureau",
    "NIA", "National Investigation Agency",
    "ATS", "Anti-Terrorism Squad",

    # ---- State Police / Specialised -----------------------------------------
    "SOG", "Special Operations Group",
    "J&K Police", "Jammu and Kashmir Police",
    "STF", "Special Task Force",
    "State Police", "Local Police",
]

# ============================================================================
# 7.  THREAT CATEGORIES & SEVERITY LEVELS
# ============================================================================

THREAT_CATEGORIES: List[str] = [
    "Terrorism",
    "Insurgency",
    "Cross-Border Infiltration",
    "Naxal/Maoist",
    "Communal Violence",
    "Cyber Attack",
    "Maritime Security",
    "Border Skirmish",
    "Espionage",
    "CBRN",  # Chemical, Biological, Radiological, Nuclear
]

SEVERITY_LEVELS: List[str] = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]

# ============================================================================
# 8.  LOOKUP MAPS  (derived — built once at import time)
# ============================================================================

# 8a.  Active countries set ---------------------------------------------------
ACTIVE_COUNTRIES: Set[str] = set(SOUTH_ASIA_COUNTRIES)

# 8b.  City → Country (lowercase keys for case-insensitive matching) ----------
CITY_TO_COUNTRY_MAP: Dict[str, str] = {}
for _country, _cities in COUNTRY_TO_CITIES.items():
    for _city in _cities:
        CITY_TO_COUNTRY_MAP[_city.lower()] = _country

# 8c.  Country set (lowercase) -----------------------------------------------
COUNTRY_SET_LOWER: Set[str] = {c.lower() for c in ACTIVE_COUNTRIES}

# 8d.  District / City → State map (Indian locations only) --------------------
#      Maps each city name (lowercase) to its corresponding state/UT.
#      Built from the sub-lists so we know the regional grouping.

_CITY_STATE_SOURCES: List[tuple] = [
    (_INDIA_JK,              "Jammu and Kashmir"),
    (_INDIA_LADAKH,          "Ladakh"),
    # Northeast — attribute to individual states where possible
    # Manipur
    (["Imphal", "Churachandpur", "Ukhrul", "Thoubal", "Tamenglong"], "Manipur"),
    # Nagaland
    (["Kohima", "Dimapur", "Mokokchung", "Mon"], "Nagaland"),
    # Mizoram
    (["Aizawl", "Champhai", "Lunglei"], "Mizoram"),
    # Meghalaya
    (["Shillong", "Tura"], "Meghalaya"),
    # Arunachal Pradesh
    (["Itanagar", "Tawang", "Bomdila", "Ziro", "Pasighat"], "Arunachal Pradesh"),
    # Tripura
    (["Agartala", "Udaipur"], "Tripura"),
    # Sikkim
    (["Gangtok", "Namchi"], "Sikkim"),
    # Assam
    (["Guwahati", "Dispur", "Dibrugarh", "Silchar", "Tezpur",
      "Jorhat", "Nagaon", "Tinsukia", "Bongaigaon"], "Assam"),
    # Chhattisgarh (Naxal)
    (["Raipur", "Jagdalpur", "Bastar", "Dantewada", "Sukma",
      "Bijapur", "Narayanpur", "Kanker", "Kondagaon"], "Chhattisgarh"),
    # Jharkhand (Naxal)
    (["Ranchi", "Latehar", "Gumla", "Bokaro", "Jamshedpur",
      "Hazaribagh", "Palamu", "Chatra"], "Jharkhand"),
    # Maharashtra (Naxal-affected districts)
    (["Gadchiroli", "Gondia"], "Maharashtra"),
    # Odisha (Naxal-affected districts)
    (["Malkangiri", "Koraput", "Rayagada"], "Odisha"),
    # Telangana fringe
    (["Bhadrachalam"], "Telangana"),
    # Delhi NCT
    (["New Delhi", "Delhi"], "Delhi"),
    # Maharashtra metros
    (["Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad", "Thane"], "Maharashtra"),
    # West Bengal
    (["Kolkata", "Siliguri", "Asansol", "Durgapur"], "West Bengal"),
    # Tamil Nadu
    (["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem"], "Tamil Nadu"),
    # Karnataka
    (["Bengaluru", "Mysuru", "Hubballi", "Mangaluru", "Belagavi"], "Karnataka"),
    # Telangana
    (["Hyderabad", "Warangal", "Nizamabad", "Karimnagar"], "Telangana"),
    # Andhra Pradesh
    (["Amaravati", "Visakhapatnam", "Vijayawada", "Tirupati",
      "Guntur", "Kurnool"], "Andhra Pradesh"),
    # Gujarat
    (["Gandhinagar", "Ahmedabad", "Surat", "Vadodara",
      "Rajkot", "Bhavnagar"], "Gujarat"),
    # Rajasthan
    (["Jaipur", "Jodhpur", "Udaipur", "Kota", "Ajmer",
      "Bikaner", "Jaisalmer", "Barmer"], "Rajasthan"),
    # Uttar Pradesh
    (["Lucknow", "Varanasi", "Agra", "Kanpur", "Prayagraj", "Meerut",
      "Noida", "Ghaziabad", "Gorakhpur", "Mathura", "Aligarh",
      "Ayodhya"], "Uttar Pradesh"),
    # Bihar
    (["Patna", "Gaya", "Bhagalpur", "Muzaffarpur", "Darbhanga"], "Bihar"),
    # Madhya Pradesh
    (["Bhopal", "Indore", "Gwalior", "Jabalpur", "Ujjain"], "Madhya Pradesh"),
    # Punjab (Chandigarh shared UT — mapped under both)
    (["Chandigarh", "Amritsar", "Ludhiana", "Jalandhar", "Patiala",
      "Pathankot", "Bathinda", "Fazilka"], "Punjab"),
    # Haryana
    (["Gurugram", "Faridabad", "Karnal", "Panipat",
      "Ambala", "Hisar"], "Haryana"),
    # Uttarakhand
    (["Dehradun", "Haridwar", "Rishikesh", "Nainital",
      "Haldwani"], "Uttarakhand"),
    # Himachal Pradesh
    (["Shimla", "Dharamshala", "Manali", "Kullu", "Mandi"], "Himachal Pradesh"),
    # Kerala
    (["Thiruvananthapuram", "Kochi", "Kozhikode", "Thrissur",
      "Kannur"], "Kerala"),
    # Goa
    (["Panaji", "Margao", "Vasco da Gama"], "Goa"),
    # Odisha (state capitals / metros)
    (["Bhubaneswar", "Cuttack", "Puri", "Rourkela", "Sambalpur"], "Odisha"),
    # Border / strategic — attribute to respective states
    (["Wagah"], "Punjab"),
    (["Uri"], "Jammu and Kashmir"),
    (["Turtuk", "Demchok", "Pangong", "Galwan", "Depsang",
      "Hot Springs", "Gogra"], "Ladakh"),
    (["Nathu La", "Doklam", "Chumbi"], "Sikkim"),
    (["Moreh"], "Manipur"),
    # Union Territory cities
    (["Port Blair"], "Andaman and Nicobar Islands"),
    (["Silvassa", "Daman", "Diu"], "Dadra and Nagar Haveli and Daman and Diu"),
    (["Kavaratti"], "Lakshadweep"),
    (["Puducherry"], "Puducherry"),
]

DISTRICT_TO_STATE_MAP: Dict[str, str] = {}
for _city_list, _state in _CITY_STATE_SOURCES:
    for _city in _city_list:
        # First mapping wins (avoids overwriting more specific entries)
        if _city.lower() not in DISTRICT_TO_STATE_MAP:
            DISTRICT_TO_STATE_MAP[_city.lower()] = _state

# 8e.  Conflict-zone flattened set (lowercase) --------------------------------
CONFLICT_ZONE_SET: Set[str] = set()
for _zone_locations in CONFLICT_ZONES.values():
    for _loc in _zone_locations:
        CONFLICT_ZONE_SET.add(_loc.lower())

# ---------------------------------------------------------------------------
# Clean up module-level loop variables so they don't pollute the namespace
# ---------------------------------------------------------------------------
del _country, _cities, _city, _city_list, _state, _zone_locations, _loc
