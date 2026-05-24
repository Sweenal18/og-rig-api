from datetime import date, timedelta, datetime
import random

SEED      = 42
SIM_START = date(2024, 1, 1)

# ── Raw lookup maps (strings, not IDs) ──────────────────────
REGIONS = {
    "RIG-001": "Permian",    "RIG-002": "Permian",
    "RIG-003": "Permian",    "RIG-004": "Permian",
    "RIG-005": "Eagle Ford", "RIG-006": "Eagle Ford",
    "RIG-007": "Eagle Ford", "RIG-008": "Eagle Ford",
    "RIG-009": "Bakken",     "RIG-010": "Bakken",
    "RIG-011": "Bakken",     "RIG-012": "Bakken",
    "RIG-013": "Marcellus",  "RIG-014": "Marcellus",
    "RIG-015": "Marcellus",  "RIG-016": "Marcellus",
    "RIG-017": "Gulf",       "RIG-018": "Gulf",
    "RIG-019": "Gulf",       "RIG-020": "Gulf",
}

WELLS = {
    "RIG-001": ["Well 001", "Well 002", "Well 003"],
    "RIG-002": ["Well 004", "Well 005", "Well 006"],
    "RIG-003": ["Well 007", "Well 008", "Well 009"],
    "RIG-004": ["Well 010", "Well 011", "Well 012"],
    "RIG-005": ["Well 013", "Well 014", "Well 015"],
    "RIG-006": ["Well 016", "Well 017", "Well 018"],
    "RIG-007": ["Well 019", "Well 020", "Well 021"],
    "RIG-008": ["Well 022", "Well 023", "Well 024"],
    "RIG-009": ["Well 025", "Well 026", "Well 027"],
    "RIG-010": ["Well 028", "Well 029", "Well 030"],
    "RIG-011": ["Well 031", "Well 032", "Well 033"],
    "RIG-012": ["Well 034", "Well 035", "Well 036"],
    "RIG-013": ["Well 037", "Well 038", "Well 039"],
    "RIG-014": ["Well 040", "Well 041", "Well 042"],
    "RIG-015": ["Well 043", "Well 044", "Well 045"],
    "RIG-016": ["Well 046", "Well 047", "Well 048"],
    "RIG-017": ["Well 049", "Well 050", "Well 051"],
    "RIG-018": ["Well 052", "Well 053", "Well 054"],
    "RIG-019": ["Well 055", "Well 056", "Well 057"],
    "RIG-020": ["Well 058", "Well 059", "Well 060"],
}

REGION_PARAMS = {
    "Permian":    {"uptime": 0.92, "rop": 85.0, "cost": 28000},
    "Eagle Ford": {"uptime": 0.88, "rop": 75.0, "cost": 30000},
    "Bakken":     {"uptime": 0.82, "rop": 65.0, "cost": 32000},
    "Marcellus":  {"uptime": 0.78, "rop": 60.0, "cost": 35000},
    "Gulf":       {"uptime": 0.85, "rop": 70.0, "cost": 45000},
}

STATUSES         = ["Active Drilling", "Standby", "NPT",
                    "Rigging Up", "Rigging Down"]
DOWNTIME_REASONS = ["Equipment Failure", "Human Error",
                    "Maintenance Delay", "Waiting on Weather",
                    "Regulatory Hold", "Third Party Delay",
                    "Supply Chain Delay"]
COST_CATEGORIES  = ["Bit Costs", "Mud Chemicals", "Crew Day Rate",
                    "Rig Day Rate", "Equipment Repair",
                    "Preventive Maintenance", "Corrective Maintenance",
                    "Supply Chain"]
EQUIPMENT_TYPES  = ["Top Drive", "Mud Pump", "Draw Works",
                    "BOP", "Generator"]
FAILURE_TYPES    = {
    "Top Drive":  ["Top Drive Failure"],
    "Mud Pump":   ["Mud Pump Failure"],
    "Draw Works": ["Draw Works Failure"],
    "BOP":        ["BOP Malfunction"],
    "Generator":  ["Generator Failure"],
}
MAINTENANCE_TYPES = ["Preventive", "Corrective", "Predictive"]
CONTRACTORS       = ["Halliburton", "Baker Hughes",
                     "Schlumberger", "Patterson-UTI", "NOV"]
INCIDENT_TYPES    = ["Near Miss", "First Aid", "Lost Time Injury",
                     "Spill", "Equipment Damage",
                     "Dropped Object", "Emission Breach"]
INCIDENT_STATUSES = ["Open", "Under Investigation", "Closed"]
WELL_TYPES        = ["Horizontal", "Vertical", "Directional"]
CREW_IDS          = {
    "Permian":    [f"CREW-{i:03d}" for i in range(1,  11)],
    "Eagle Ford": [f"CREW-{i:03d}" for i in range(11, 21)],
    "Bakken":     [f"CREW-{i:03d}" for i in range(21, 31)],
    "Marcellus":  [f"CREW-{i:03d}" for i in range(31, 41)],
    "Gulf":       [f"CREW-{i:03d}" for i in range(41, 51)],
}
RIG_COMMISSION = {}

def _init_rig_commission():
    rng = random.Random(SEED)
    for rig_id in REGIONS:
        RIG_COMMISSION[rig_id] = rng.randint(2010, 2022)

_init_rig_commission()

def _seasonal_factor(month: int) -> float:
    if month in [1, 2, 3]: return 0.93
    if month in [7, 8, 9]: return 0.96
    return 1.0

def _recorded_at(d: date, hour: int, minute: int) -> str:
    return datetime(d.year, d.month, d.day,
                    hour, minute, 0).strftime("%Y-%m-%dT%H:%M:%SZ")

def _all_dates(from_date: date, to_date: date):
    current = from_date
    while current <= to_date:
        yield current
        current += timedelta(days=1)

def get_sim_end() -> date:
    return date.today() - timedelta(days=1)

def generate_rig_readings(from_date: date, to_date: date) -> list[dict]:
    import numpy as np
    rows = []
    for d in _all_dates(from_date, to_date):
        seed = int(d.strftime("%Y%m%d"))
        rng  = random.Random(seed)
        np.random.seed(seed)
        for rig_id, region in REGIONS.items():
            p         = REGION_PARAMS[region]
            sf        = _seasonal_factor(d.month)
            drill_hrs = float(np.clip(
                np.random.normal(24 * p["uptime"] * sf, 1.5), 0, 24))
            down_hrs  = round(24.0 - drill_hrs, 2)
            npt_hrs   = round(down_hrs * float(
                np.random.uniform(0.3, 0.8)), 2) if down_hrs > 0 else 0.0
            rop       = float(np.clip(
                np.random.normal(p["rop"] * sf, 8), 10, 200))
            cost      = float(np.random.normal(p["cost"], p["cost"] * 0.05))
            status    = "Active Drilling" if drill_hrs > 20 else (
                        "NPT" if down_hrs > 16 else "Standby")
            dr        = rng.choice(DOWNTIME_REASONS) if down_hrs > 2 else None
            rows.append({
                "rig_id":          rig_id,
                "recorded_at":     _recorded_at(d, 23, 59),
                "well_name":       rng.choice(WELLS[rig_id]),
                "well_type":       rng.choice(WELL_TYPES),
                "status":          status,
                "downtime_reason": dr,
                "cost_category":   rng.choice(COST_CATEGORIES),
                "drilling_hours":  round(drill_hrs, 2),
                "downtime_hours":  down_hrs,
                "npt_hours":       npt_hrs,
                "rop_ft_hr":       round(rop, 2),
                "cost_per_day":    round(cost, 2),
                "sla_met":         1 if drill_hrs >= 20 else 0,
            })
    return rows

def generate_equipment_events(from_date: date, to_date: date) -> list[dict]:
    rows = []
    for d in _all_dates(from_date, to_date):
        seed = int(d.strftime("%Y%m%d")) + 1000
        rng  = random.Random(seed)
        for rig_id in REGIONS:
            age_factor = (d.year - RIG_COMMISSION[rig_id]) / 14
            for eq_type in EQUIPMENT_TYPES:
                fail_prob = 0.03 + (age_factor * 0.04)
                failed    = 1 if rng.random() < fail_prob else 0
                down_hrs  = round(rng.expovariate(1/4), 2) if failed else 0.0
                res_hrs   = round(down_hrs * rng.uniform(1.2, 2.5), 2) if failed else 0.0
                rows.append({
                    "event_id":            f"EVT-{d.strftime('%Y%m%d')}-{rig_id}-{eq_type.replace(' ','')}",
                    "rig_id":              rig_id,
                    "recorded_at":         _recorded_at(d, rng.randint(0, 23), rng.randint(0, 59)),
                    "equipment_type":      eq_type,
                    "failure_flag":        failed,
                    "failure_type":        rng.choice(FAILURE_TYPES[eq_type]) if failed else None,
                    "downtime_caused_hrs": down_hrs,
                    "sla_met":             1 if res_hrs <= 8 else 0,
                    "resolution_hrs":      res_hrs,
                })
    return rows

def generate_maintenance(from_date: date, to_date: date) -> list[dict]:
    rows = []
    for d in _all_dates(from_date, to_date):
        seed = int(d.strftime("%Y%m%d")) + 2000
        rng  = random.Random(seed)
        for rig_id, region in REGIONS.items():
            for eq_type in EQUIPMENT_TYPES:
                if rng.random() < 0.10:
                    m_type = rng.choices(
                        MAINTENANCE_TYPES, weights=[50, 35, 15])[0]
                    rows.append({
                        "maintenance_id":   f"MNT-{d.strftime('%Y%m%d')}-{rig_id}-{eq_type.replace(' ','')}",
                        "rig_id":           rig_id,
                        "recorded_at":      _recorded_at(d, rng.randint(6, 18), rng.randint(0, 59)),
                        "equipment_type":   eq_type,
                        "maintenance_type": m_type,
                        "contractor_name":  rng.choice(CONTRACTORS),
                        "duration_hrs":     round(rng.uniform(1, 12), 2),
                        "cost":             round(rng.uniform(500, 15000), 2),
                        "technician_count": rng.randint(1, 4),
                    })
    return rows

def generate_crew_hours(from_date: date, to_date: date) -> list[dict]:
    rows = []
    for d in _all_dates(from_date, to_date):
        seed = int(d.strftime("%Y%m%d")) + 3000
        rng  = random.Random(seed)
        for rig_id, region in REGIONS.items():
            for shift in ["Day", "Night"]:
                hour = 18 if shift == "Night" else 6
                rows.append({
                    "rig_id":         rig_id,
                    "recorded_at":    _recorded_at(d, hour, 0),
                    "crew_id":        rng.choice(CREW_IDS[region]),
                    "shift":          shift,
                    "hours_worked":   round(rng.normalvariate(12, 0.5), 2),
                    "overtime_hours": round(rng.uniform(0, 2), 2) if rng.random() < 0.15 else 0.0,
                    "is_present":     1,
                    "npt_attributed": 1 if rng.random() < 0.05 else 0,
                })
    return rows

def generate_incidents(from_date: date, to_date: date) -> list[dict]:
    rows = []
    for d in _all_dates(from_date, to_date):
        seed = int(d.strftime("%Y%m%d")) + 4000
        rng  = random.Random(seed)
        for rig_id, region in REGIONS.items():
            if rng.random() < 0.085:
                inc_type = rng.choices(
                    INCIDENT_TYPES,
                    weights=[35,25,5,8,15,10,2])[0]
                rows.append({
                    "incident_id":         f"INC-{d.strftime('%Y%m%d')}-{rig_id}",
                    "rig_id":              rig_id,
                    "recorded_at":         _recorded_at(d, rng.randint(0, 23), rng.randint(0, 59)),
                    "crew_id":             rng.choice(CREW_IDS[region]),
                    "incident_type":       inc_type,
                    "equipment_type":      rng.choice(EQUIPMENT_TYPES + [None]),
                    "incident_status":     rng.choices(
                        INCIDENT_STATUSES, weights=[20,30,50])[0],
                    "downtime_caused_hrs": round(rng.uniform(0, 8), 2) if inc_type in [
                        "Lost Time Injury","Spill","Emission Breach"] else 0.0,
                    "is_recordable":       1 if inc_type in [
                        "Lost Time Injury","Spill","Emission Breach"] else 0,
                })
    return rows
