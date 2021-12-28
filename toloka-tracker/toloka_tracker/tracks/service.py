from fastapi import HTTPException, status

from toloka_tracker.dashboards.data import DashboardsTracksDatabase
from toloka_tracker.dashboards.models import AddTrackRequest, RemoveTrackRequest
from toloka_tracker.tracks.data import TracksDatabase
from toloka_tracker.tracks.models import Track


def store_track(track: Track, db):
    db_tracks = TracksDatabase(
        name=track.name,
        toloka_project_id=track.toloka_project_id,
        max_parallel_pools=track.max_parallel_pools,
        min_pool_acceptance_rate=track.min_pool_acceptance_rate,
        max_hourly_appeals=track.max_hourly_appeals
    )

    db.add(db_tracks)
    db.commit()
    db.refresh(db_tracks)
    return db_tracks


def remove_track_from_db(track_id: int, db):
    db_tracks = db.query(TracksDatabase).filter(TracksDatabase.id == track_id).first()
    if not db_tracks:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Track not found")
    db.delete(db_tracks)
    db.commit()
    db.refresh(db_tracks)

    related_tracks = db.query(DashboardsTracksDatabase).filter(DashboardsTracksDatabase.track_id == db_tracks).all()
    for track_to_dashboard in related_tracks:
        db.delete(track_to_dashboard)
        db.commit()
        db.refresh(track_to_dashboard)

    return db_tracks


def get_track_by_id(db, track_id: int):
    track = db.query(TracksDatabase).filter(TracksDatabase.id == track_id).first()

    if not track:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No tracks found by id",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "id": track.id,
        "project_id": track.toloka_project_id,
        "max_parallel_pools": track.max_parallel_pools,
        "min_pool_acceptance_rate": track.min_pool_acceptance_rate,
        "max_hourly_appeals": track.max_hourly_appeals
    }


def get_all_tracks(db):
    tracks = db.query(TracksDatabase).all()

    result = []

    for track in tracks:
        result.append({
            "id": track.id,
            "project_id": track.toloka_project_id,
            "max_parallel_pools": track.max_parallel_pools,
            "min_pool_acceptance_rate": track.min_pool_acceptance_rate,
            "max_hourly_appeals": track.max_hourly_appeals
        })


def add_track_to_dashboard(request: AddTrackRequest, db):
    db_tracks = DashboardsTracksDatabase(request.track_id, request.dashboard_id)
    db.add(db_tracks)
    db.commit()
    db.refresh(db_tracks)
    return db_tracks


def remove_track_from_dashboard(request: RemoveTrackRequest, db):
    db_tracks = DashboardsTracksDatabase(request.track_id, request.dashboard_id)
    db.delete(db_tracks)
    db.commit()
    db.refresh(db_tracks)
    return db_tracks
