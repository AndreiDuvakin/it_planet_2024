from sqlalchemy import Column, Integer, String

from .connect import base


class RegionType(base):
    __tablename__ = 'region_types'

    id = Column(Integer, primary_key=True)
    type = Column(String)
