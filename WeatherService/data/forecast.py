from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime

from .connect import base


class Forecast(base):
    __tablename__ = 'forecasts'

    id = Column(Integer, primary_key=True)
    date_time = Column(DateTime, nullable=False)
    temperature = Column(Float)
    weather_condition = Column(String, nullable=False)
    region_id = Column(Integer, ForeignKey('regions.id'))
