from sqlalchemy import Column, Integer, String, ForeignKey, Float

from .connect import base


class Region(base):
    __tablename__ = 'regions'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    parent_region = Column(Integer, ForeignKey('regions.id'))
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    account_id = Column(Integer, ForeignKey('accounts.id'))
    type_id = Column(Integer, ForeignKey('region_types.id'))
