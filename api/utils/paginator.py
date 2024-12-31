from math import ceil

def paginate_items(items, page: int = 1, per_page: int = 10):
    """Function to paginate a list of items."""
    
    total_items = len(items)
    total_pages = ceil(total_items / per_page)
    
    if page > total_pages:
        page = total_pages  # Set the page to the last page if it exceeds the total pages
    
    start = (page - 1) * per_page
    end = start + per_page
    paginated_items = items[start:end]

    return {
        "data": paginated_items,
        "current_page": page,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }
