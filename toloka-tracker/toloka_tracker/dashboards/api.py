from dependency_injector.wiring import inject, Provide
from fastapi import Depends, APIRouter, Request

from dependencies import Container, Service
from toloka_tracker.auth.service import get_current_user
from toloka_tracker.dashboards.models import Dashboard, DashboardResponse, AddTrackRequest, RemoveDashboardRequest, \
    AddRoleRequest
from toloka_tracker.dashboards.service import store_dashboard, get_dashboard_by_id, add_track_to_dashboard, remove_dashboard

dashboards_router = APIRouter()


@dashboards_router.get("/dashboards/{dashboard_id}", response_model=DashboardResponse)
@inject
async def get_dashboard(request: Request, dashboard_id: int, current_user=Depends(get_current_user), db: Service = Depends(Provide[Container.db])):
    return get_dashboard_by_id(db=next(db.get_db()), dashboard_id=dashboard_id, user_id=current_user.id)


@dashboards_router.post("/dashboards/create")
@inject
def create_dashboard(dashboard: Dashboard, current_user=Depends(get_current_user), db: Service = Depends(Provide[Container.db])):
    return store_dashboard(dashboard, next(db.get_db()), current_user.id)


@dashboards_router.post("/dashboards/remove")
@inject
def create_dashboard(dashboard: RemoveDashboardRequest, current_user=Depends(get_current_user), db: Service = Depends(Provide[Container.db])):
    return remove_dashboard(dashboard, next(db.get_db()), current_user.id)


@dashboards_router.post("/dashboards/add_track")
@inject
def add_track_to_dashboard(add_request: AddTrackRequest, current_user=Depends(get_current_user), db: Service = Depends(Provide[Container.db])):
    return add_track_to_dashboard(add_request, next(db.get_db()), current_user.id)


@dashboards_router.post("/dashboards/add_acl")
@inject
def add_role_to_dashboard(add_request: AddRoleRequest, current_user=Depends(get_current_user), db: Service = Depends(Provide[Container.db])):
    return a(add_request, next(db.get_db()), current_user.id)