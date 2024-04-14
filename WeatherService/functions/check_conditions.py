def is_current_conditions(condition) -> bool:
    valid_conditions = {"CLEAR", "CLOUDY", "RAIN", "SNOW", "FOG", "STORM"}
    if condition not in valid_conditions:
        return False
    return True