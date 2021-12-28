from dependency_injector.wiring import inject, Provide
from fastapi import Depends, APIRouter

from dependencies import Container, Service
from toloka_tracker.auth.service import get_current_user
from toloka_tracker.tracks.models import Track, TrackResponse
from toloka_tracker.tracks.service import remove_track_from_db, store_track, get_track_by_id

tracks_router = APIRouter()


@tracks_router.get("/tracks/{track_id}", response_model=TrackResponse)
@inject
async def get_track(track_id: int, current_user=Depends(get_current_user), db: Service = Depends(Provide[Container.db])):
    return get_track_by_id(db=next(db.get_db()), track_id=track_id)


@tracks_router.post("/tracks/create")
@inject
def create_track(track: Track, current_user=Depends(get_current_user), db: Service = Depends(Provide[Container.db])):
    return store_track(track, next(db.get_db()))


@tracks_router.post("/tracks/remove")
@inject
def remove_track(track_id: int, current_user=Depends(get_current_user), db: Service = Depends(Provide[Container.db])):
    return remove_track_from_db(track_id, next(db.get_db()))