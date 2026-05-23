from math import ceil

def paginate(data: list, page: int, page_size: int) -> dict:
    total_records = len(data)
    total_pages   = ceil(total_records / page_size) if total_records > 0 else 1
    start         = (page - 1) * page_size
    end           = start + page_size
    page_data     = data[start:end]
    has_next      = page < total_pages
    return {
        "page":          page,
        "page_size":     page_size,
        "total_records": total_records,
        "total_pages":   total_pages,
        "has_next":      has_next,
        "next_page":     page + 1 if has_next else None,
        "data":          page_data,
    }
