def check_temperature_wind_speed_precipitation_amount(temperature, wind_speed, precipitation_amount):
    try:
        if temperature < 0 or wind_speed < 0 or precipitation_amount < 0:
            return False
        return True
    except ValueError:
        return False