from sqlalchemy import Column, Integer, String, ForeignKey, Float

from .connect import base


class Region(base):
    __tablename__ = 'regions'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    parent_region = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    account_id = Column(Integer, ForeignKey('accounts.id'))
    type_id = Column(Integer, ForeignKey('region_types.id'))
