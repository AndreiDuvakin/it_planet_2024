from sqlalchemy import Column, Integer, ForeignKey

from .connect import base


class WeatherForecast(base):
    __tablename__ = 'weather_forecasts'

    id = Column(Integer, primary_key=True)
    weather_id = Column(Integer, ForeignKey('weathers.id'))
    forecast_id = Column(Integer, ForeignKey('forecasts.id'))
