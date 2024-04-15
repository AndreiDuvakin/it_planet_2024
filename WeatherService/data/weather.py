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
    measurement_date_time = Column(DateTime, nullable=False)
    region_id = Column(Integer, ForeignKey('regions.id'))


