def is_current_region_id(region_id: int):
    try:
        if region_id is None or int(region_id) <= 0:
            return False
        return True
    except ValueError:
        return False
