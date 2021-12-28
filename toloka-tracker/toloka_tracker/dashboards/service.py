from fastapi import HTTPException, status

from toloka_tracker.dashboards.data import DashboardsDatabase, DashboardsRolesDatabase, DashboardsTracksDatabase
from toloka_tracker.dashboards.models import Dashboard, AddTrackRequest, RemoveDashboardRequest, RemoveTrackRequest, \
    AddRoleRequest
from toloka_tracker.tracks.data import TracksDatabase
from toloka_tracker.users.service import get_user_by_id


def store_dashboard(dashboard: Dashboard, db, user_id: int):
    db_dashboards: DashboardsDatabase = DashboardsDatabase(name=dashboard.name, owmer_user_id=dashboard.owner_user_id)
    db.add(db_dashboards)
    db.commit()
    db.refresh(db_dashboards)

    db_dashboards_roles = DashboardsRolesDatabase(dashboard_id=db_dashboards.id, user_id=user_id, role="owner")
    db.add(db_dashboards_roles)
    db.commit()
    db.refresh(db_dashboards_roles)
    return db_dashboards


def store_role(request: AddRoleRequest, db, user_id: int):
    if not check_roles(db, request.dashboard_id, user_id, ["owner", "admin"]):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Only admin can add ACL")

    if request.role == "owner":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Only one owner can exists")

    db_dashboards_roles = DashboardsRolesDatabase(dashboard_id=request.dashboard_id, user_id=user_id, role=request.role)
    db.add(db_dashboards_roles)
    db.commit()
    db.refresh(db_dashboards_roles)
    return db_dashboards_roles


def remove_dashboard(request: RemoveDashboardRequest, db, user_id: int):
    if not check_roles(db, request.dashboard_id, user_id, ["owner"]):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Only owner can remove dashboard")

    db_dashboards: DashboardsDatabase = db.query(DashboardsDatabase).filter(DashboardsDatabase.id == request.dashboard_id).first()
    if not db_dashboards:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dashboard not found")

    if db_dashboards.owner_user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Only owner can remove dashboard")

    db.delete(db_dashboards)
    db.commit()
    db.refresh(db_dashboards)

    related_tracks = db.query(DashboardsTracksDatabase).filter(DashboardsTracksDatabase.dashboard_id == request.dashboard_id).all()
    for track_to_dashboard in related_tracks:
        db.delete(track_to_dashboard)
        db.commit()
        db.refresh(track_to_dashboard)

    return db_dashboards


def get_dashboard_by_id(db, dashboard_id: int, user_id: int):
    role = db.query(DashboardsRolesDatabase) \
        .filter(DashboardsRolesDatabase.dashboard_id == dashboard_id) \
        .filter(DashboardsRolesDatabase.user_id == user_id).first()

    if not role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not enough permissions",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = {}
    dashboard = db.query(DashboardsDatabase).filter(DashboardsDatabase.id == dashboard_id).first()
    owner_user = get_user_by_id(db, dashboard.owner_user_id)['login']
    result["dashboard_name"] = dashboard.name
    result["dashboard_owner"] = owner_user.login
    result['tracks'] = []
    tracks = db.query(TracksDatabase).filter(TracksDatabase.dashboard_id == dashboard_id).all()

    for track in tracks:
        result['tracks'].append({
            "track_name": track.name,
            "toloka_project": track.toloka_project_id,
            "max_parallel_pools": track.max_parallel_pools,
            "max_hourly_appeals": track.max_hourly_appeals,
            "min_pool_acceptance_rate": track.min_pool_acceptance_rate,
        })

    return result


def check_roles(db, dashboard_id, user_id, roles):
    role = db.query(DashboardsRolesDatabase) \
        .filter(DashboardsRolesDatabase.dashboard_id == dashboard_id) \
        .filter(DashboardsRolesDatabase.user_id == user_id).first()

    return role in roles


def add_track_to_dashboard(request: AddTrackRequest, db, user_id: int):
    if not check_roles(db, request.dashboard_id, user_id, ["owner", "admin"]):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Only owner or admin can add track")

    db_tracks = DashboardsTracksDatabase(request.track_id, request.dashboard_id)
    db.add(db_tracks)
    db.commit()
    db.refresh(db_tracks)
    return db_tracks


def remove_track_from_dashboard(request: RemoveTrackRequest, db, user_id):
    if not check_roles(db, request.dashboard_id, user_id, ["owner", "admin"]):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Only owner or admin can remove track")
    db_tracks = DashboardsTracksDatabase(request.track_id, request.dashboard_id)
    db.delete(db_tracks)
    db.commit()
    db.refresh(db_tracks)
    return db_tracks
