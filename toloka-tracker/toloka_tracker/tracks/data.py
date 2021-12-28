from sqlalchemy import Column, Integer, String, ForeignKey, Float
from dependencies import Base


class TracksDatabase(Base):
    __tablename__ = "tracks"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    toloka_project_id = Column(String)
    max_parallel_pools = Column(Integer)
    min_pool_acceptance_rate = Column(Float)
    max_hourly_appeals = Column(Integer)
