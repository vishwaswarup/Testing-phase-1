"""
Test Phase 2 Deduplication
"""
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, os.path.join(PROJECT_ROOT, "src", "drdo_phase1"))

from models.incident import Incident
from deduplication import IncidentDatabase

def test_deduplication():
    db = IncidentDatabase()
    
    inc1 = Incident(
        incident_id="inc-1",
        date="2025-01-01",
        country="India",
        killed=5,
        injured=10,
        weapon_types=["Explosives"]
    )
    
    # Matching date and country, should merge
    inc2 = Incident(
        incident_id="inc-2",
        date="2025-01-01",
        country="India",
        killed=2,
        injured=15,
        weapon_types=["Firearms"]
    )
    
    # Different date, should not merge
    inc3 = Incident(
        incident_id="inc-3",
        date="2025-01-02",
        country="India",
        killed=0,
        injured=0
    )
    
    res1 = db.add_incident(inc1)
    res2 = db.add_incident(inc2)
    res3 = db.add_incident(inc3)
    
    assert len(db.incidents) == 2, f"Expected 2 incidents, got {len(db.incidents)}"
    assert db.incidents[0].killed == 5, "Failed to max killed casualties"
    assert db.incidents[0].injured == 15, "Failed to max injured casualties"
    assert set(db.incidents[0].weapon_types) == {"Explosives", "Firearms"}, "Failed to merge weapons"
    
    print("Deduplication test passed successfully!")

if __name__ == "__main__":
    test_deduplication()
