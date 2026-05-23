from fastapi import FastAPI, Query, HTTPException
from datetime import date, datetime
from generator import (
    generate_rig_readings,
    generate_equipment_events,
    generate_maintenance,
    generate_crew_hours,
    generate_incidents,
    get_sim_end,
    SIM_START,
)
from pagination import paginate
from models import PaginatedResponse

app = FastAPI(
    title="O&G Rig Operations API",
    description="Simulated source systems for the H&P Rig Operations Intelligence Platform",
    version="1.0.0",
)

def validate_dates(from_date: date) -> tuple[date, date]:
    sim_end = get_sim_end()
    if from_date < SIM_START:
        raise HTTPException(400, f"from_date cannot be before {SIM_START}")
    if from_date > sim_end:
        raise HTTPException(400, f"from_date cannot be after {sim_end} - no data yet")
    return from_date, sim_end


@app.get("/")
def root():
    return {
        "api":        "O&G Rig Operations Intelligence Platform",
        "version":    "1.0.0",
        "sim_start":  str(SIM_START),
        "sim_end":    str(get_sim_end()),
        "endpoints": [
            "/scada/rig-readings",
            "/scada/equipment-events",
            "/sap-pm/maintenance",
            "/erp/crew",
            "/hse/incidents",
        ],
    }


@app.get("/scada/rig-readings", response_model=PaginatedResponse)
def rig_readings(
    from_date: date = Query(default=SIM_START, description="Start date YYYY-MM-DD"),
    page:      int  = Query(default=1, ge=1),
    page_size: int  = Query(default=500, ge=1, le=1000),
):
    from_date, to_date = validate_dates(from_date)
    data   = generate_rig_readings(from_date, to_date)
    paged  = paginate(data, page, page_size)
    return PaginatedResponse(
        endpoint="scada_rig_readings",
        from_date=str(from_date),
        **paged,
    )


@app.get("/scada/equipment-events", response_model=PaginatedResponse)
def equipment_events(
    from_date: date = Query(default=SIM_START, description="Start date YYYY-MM-DD"),
    page:      int  = Query(default=1, ge=1),
    page_size: int  = Query(default=500, ge=1, le=1000),
):
    from_date, to_date = validate_dates(from_date)
    data   = generate_equipment_events(from_date, to_date)
    paged  = paginate(data, page, page_size)
    return PaginatedResponse(
        endpoint="scada_equipment_events",
        from_date=str(from_date),
        **paged,
    )


@app.get("/sap-pm/maintenance", response_model=PaginatedResponse)
def maintenance(
    from_date: date = Query(default=SIM_START, description="Start date YYYY-MM-DD"),
    page:      int  = Query(default=1, ge=1),
    page_size: int  = Query(default=500, ge=1, le=1000),
):
    from_date, to_date = validate_dates(from_date)
    data   = generate_maintenance(from_date, to_date)
    paged  = paginate(data, page, page_size)
    return PaginatedResponse(
        endpoint="sap_pm_maintenance",
        from_date=str(from_date),
        **paged,
    )


@app.get("/erp/crew", response_model=PaginatedResponse)
def crew(
    from_date: date = Query(default=SIM_START, description="Start date YYYY-MM-DD"),
    page:      int  = Query(default=1, ge=1),
    page_size: int  = Query(default=500, ge=1, le=1000),
):
    from_date, to_date = validate_dates(from_date)
    data   = generate_crew_hours(from_date, to_date)
    paged  = paginate(data, page, page_size)
    return PaginatedResponse(
        endpoint="erp_crew_hours",
        from_date=str(from_date),
        **paged,
    )


@app.get("/hse/incidents", response_model=PaginatedResponse)
def incidents(
    from_date: date = Query(default=SIM_START, description="Start date YYYY-MM-DD"),
    page:      int  = Query(default=1, ge=1),
    page_size: int  = Query(default=500, ge=1, le=1000),
):
    from_date, to_date = validate_dates(from_date)
    data   = generate_incidents(from_date, to_date)
    paged  = paginate(data, page, page_size)
    return PaginatedResponse(
        endpoint="hse_incidents",
        from_date=str(from_date),
        **paged,
    )

