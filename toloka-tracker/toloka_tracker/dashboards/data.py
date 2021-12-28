from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
import datetime
from dependencies import Base


class DashboardsDatabase(Base):
    __tablename__ = "dashboards"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    owner_user_id = Column(String, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class DashboardsRolesDatabase(Base):
    __tablename__ = "dashboards_roles"

    dashboard_id = Column(Integer, ForeignKey('dashboards.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    role = Column(String)


class DashboardsTracksDatabase(Base):
    __tablename__ = "tracks_to_dashboards"

    track_id = Column(Integer, ForeignKey('tracks.id'), primary_key=True)
    dashboard_id = Column(Integer, ForeignKey('dashboards.id'), primary_key=True)