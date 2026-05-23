from pydantic import BaseModel
from typing import Any

class PaginatedResponse(BaseModel):
    endpoint: str
    from_date: str
    page: int
    page_size: int
    total_records: int
    total_pages: int
    has_next: bool
    next_page: int | None
    data: list[dict[str, Any]]
