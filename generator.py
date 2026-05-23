import numpy as np
import random
from datetime import date, timedelta

SEED = 42
SIM_START = date(2024, 1, 1)

REGION_PARAMS = {
    1: {"uptime": 0.92, "rop": 85.0, "cost": 28000},
    2: {"uptime": 0.88, "rop": 75.0, "cost": 30000},
    3: {"uptime": 0.82, "rop": 65.0, "cost": 32000},
    4: {"uptime": 0.78, "rop": 60.0, "cost": 35000},
    5: {"uptime": 0.85, "rop": 70.0, "cost": 45000},
}

RIG_REGION_MAP = {f"RIG-{i:03d}": ((i - 1) // 4) + 1 for i in range(1, 21)}
RIG_WELLS_MAP  = {f"RIG-{i:03d}": [f"WELL-{(i-1)*3+j:03d}" for j in range(1, 4)] for i in range(1, 21)}
EQUIPMENT_IDS  = ["EQ-001", "EQ-002", "EQ-003", "EQ-004", "EQ-005"]
EQ_FAILURE_MAP = {"EQ-001":[1],"EQ-002":[2],"EQ-003":[5],"EQ-004":[3],"EQ-005":[4]}
RIG_COMMISSION = {}

def _init_rig_commission():
    rng = random.Random(SEED)
    for i in range(1, 21):
        RIG_COMMISSION[f"RIG-{i:03d}"] = rng.randint(2010, 2022)

_init_rig_commission()

def _seasonal_factor(month: int) -> float:
    if month in [1, 2, 3]: return 0.93
    if month in [7, 8, 9]: return 0.96
    return 1.0

def _date_id(d: date) -> int:
    return int(d.strftime("%Y%m%d"))

def _all_dates(from_date: date, to_date: date):
    current = from_date
    while current <= to_date:
        yield current
        current += timedelta(days=1)

def get_sim_end() -> date:
    return date.today() - timedelta(days=1)

def generate_rig_readings(from_date: date, to_date: date) -> list[dict]:
    rows = []
    for d in _all_dates(from_date, to_date):
        seed = int(d.strftime("%Y%m%d"))
        rng  = random.Random(seed)
        np.random.seed(seed)
        for rig_id, region_id in RIG_REGION_MAP.items():
            p         = REGION_PARAMS[region_id]
            sf        = _seasonal_factor(d.month)
            drill_hrs = float(np.clip(np.random.normal(24 * p["uptime"] * sf, 1.5), 0, 24))
            down_hrs  = round(24.0 - drill_hrs, 2)
            npt_hrs   = round(down_hrs * float(np.random.uniform(0.3, 0.8)), 2) if down_hrs > 0 else 0.0
            rop       = float(np.clip(np.random.normal(p["rop"] * sf, 8), 10, 200))
            cost      = float(np.random.normal(p["cost"], p["cost"] * 0.05))
            status_id = 1 if drill_hrs > 20 else (3 if down_hrs > 16 else 2)
            dr_id     = rng.randint(1, 7) if down_hrs > 2 else None
            sla_met   = 1 if drill_hrs >= 20 else 0
            rows.append({
                "date_id":            _date_id(d),
                "rig_id":             rig_id,
                "region_id":          region_id,
                "well_id":            rng.choice(RIG_WELLS_MAP[rig_id]),
                "status_id":          status_id,
                "shift_id":           1,
                "downtime_reason_id": dr_id,
                "cost_category_id":   rng.choice([3, 4, 7, 8]),
                "drilling_hours":     round(drill_hrs, 2),
                "downtime_hours":     down_hrs,
                "npt_hours":          npt_hrs,
                "rop_ft_hr":          round(rop, 2),
                "cost_per_day":       round(cost, 2),
                "sla_met_flag":       sla_met,
            })
    return rows

def generate_equipment_events(from_date: date, to_date: date) -> list[dict]:
    rows     = []
    event_id = 1
    for d in _all_dates(from_date, to_date):
        seed = int(d.strftime("%Y%m%d")) + 1000
        rng  = random.Random(seed)
        for rig_id, region_id in RIG_REGION_MAP.items():
            age_factor = (d.year - RIG_COMMISSION[rig_id]) / 14
            for eq_id in EQUIPMENT_IDS:
                fail_prob = 0.03 + (age_factor * 0.04)
                failed    = 1 if rng.random() < fail_prob else 0
                down_hrs  = round(rng.expovariate(1/4), 2) if failed else 0.0
                res_hrs   = round(down_hrs * rng.uniform(1.2, 2.5), 2) if failed else 0.0
                sla_met   = 1 if res_hrs <= 8 else 0
                rows.append({
                    "event_id":            f"EVT-{_date_id(d)}-{rig_id}-{eq_id}",
                    "date_id":             _date_id(d),
                    "rig_id":              rig_id,
                    "region_id":           region_id,
                    "equipment_id":        eq_id,
                    "status_id":           9 if failed else 7,
                    "failure_type_id":     rng.choice(EQ_FAILURE_MAP[eq_id]) if failed else None,
                    "failure_flag":        failed,
                    "downtime_caused_hrs": down_hrs,
                    "sla_met_flag":        sla_met,
                    "resolution_hrs":      res_hrs,
                })
                event_id += 1
    return rows

def generate_maintenance(from_date: date, to_date: date) -> list[dict]:
    rows    = []
    maint_id = 1
    for d in _all_dates(from_date, to_date):
        seed = int(d.strftime("%Y%m%d")) + 2000
        rng  = random.Random(seed)
        for rig_id in RIG_REGION_MAP:
            region_id = RIG_REGION_MAP[rig_id]
            for eq_id in EQUIPMENT_IDS:
                if rng.random() < 0.10:
                    m_type_id = rng.choices([1, 2, 3], weights=[50, 35, 15])[0]
                    rows.append({
                        "maintenance_id":      f"MNT-{_date_id(d)}-{rig_id}-{eq_id}",
                        "date_id":             _date_id(d),
                        "rig_id":              rig_id,
                        "region_id":           region_id,
                        "equipment_id":        eq_id,
                        "maintenance_type_id": m_type_id,
                        "contractor_id":       rng.randint(1, 5),
                        "status_id":           8,
                        "duration_hrs":        round(rng.uniform(1, 12), 2),
                        "cost":                round(rng.uniform(500, 15000), 2),
                        "is_preventive":       1 if m_type_id in [1, 3] else 0,
                        "technician_count":    rng.randint(1, 4),
                    })
                    maint_id += 1
    return rows

def generate_crew_hours(from_date: date, to_date: date) -> list[dict]:
    rows = []
    region_crew = {r: [f"CREW-{((r-1)*10)+i:03d}" for i in range(1, 11)] for r in range(1, 6)}
    for d in _all_dates(from_date, to_date):
        seed = int(d.strftime("%Y%m%d")) + 3000
        rng  = random.Random(seed)
        for rig_id, region_id in RIG_REGION_MAP.items():
            for shift_id in [1, 2]:
                rows.append({
                    "date_id":             _date_id(d),
                    "rig_id":              rig_id,
                    "region_id":           region_id,
                    "crew_id":             rng.choice(region_crew[region_id]),
                    "shift_id":            shift_id,
                    "hours_worked":        round(rng.normalvariate(12, 0.5), 2),
                    "overtime_hours":      round(rng.uniform(0, 2), 2) if rng.random() < 0.15 else 0.0,
                    "is_present":          1,
                    "npt_attributed_flag": 1 if rng.random() < 0.05 else 0,
                })
    return rows

def generate_incidents(from_date: date, to_date: date) -> list[dict]:
    rows = []
    region_crew = {r: [f"CREW-{((r-1)*10)+i:03d}" for i in range(1, 11)] for r in range(1, 6)}
    for d in _all_dates(from_date, to_date):
        seed = int(d.strftime("%Y%m%d")) + 4000
        rng  = random.Random(seed)
        for rig_id, region_id in RIG_REGION_MAP.items():
            if rng.random() < 0.085:
                inc_type_id = rng.choices([1,2,3,4,5,6,7], weights=[35,25,5,8,15,10,2])[0]
                rows.append({
                    "incident_id":         f"INC-{_date_id(d)}-{rig_id}",
                    "date_id":             _date_id(d),
                    "rig_id":              rig_id,
                    "region_id":           region_id,
                    "crew_id":             rng.choice(region_crew[region_id]),
                    "incident_type_id":    inc_type_id,
                    "equipment_id":        rng.choice(EQUIPMENT_IDS + [None]),
                    "status_id":           rng.choices([11,12,13], weights=[20,30,50])[0],
                    "downtime_caused_hrs": round(rng.uniform(0, 8), 2) if inc_type_id in [3,4,7] else 0.0,
                    "is_recordable":       1 if inc_type_id in [3,4,7] else 0,
                })
    return rows
