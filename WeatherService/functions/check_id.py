def is_current_id(region_id):
    try:
        if not region_id:
            return False
        if region_id is None or int(region_id) <= 0:
            return False
        return True
    except ValueError:
        return False
