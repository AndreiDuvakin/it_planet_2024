from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime

from .connect import base


class Weather(base):
    __tablename__ = 'weathers'

    id = Column(Integer, primary_key=True)
    temperature = Column(Float)
    humidity = Column(Float)
    wind_speed = Column(Float)
    weather_condition = Column(String)
    precipitation_amount = Column(Float)
    measurement_date_time = Column(DateTime)
    region_id = Column(Integer, ForeignKey('regions.id'))


class Forecast(base):
    __tablename__ = 'forecasts'

    id = Column(Integer, primary_key=True)
    date_time = Column(DateTime)
    temperature = Column(Float)
    weather_condition = Column(String)
    region_id = Column(Integer, ForeignKey('regions.id'))


class WeatherForecast(base):
    __tablename__ = 'weather_forecast'

    id = Column(Integer, primary_key=True)
    weather_id = Column(Integer, ForeignKey('weathers.id'))
    forecast_id = Column(Integer, ForeignKey('forecasts.id'))


