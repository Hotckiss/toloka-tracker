from pydantic import BaseModel


class Dashboard(BaseModel):
    name: str
    owner_user_id: int # fk users


class DashboardRole(BaseModel):
    dashboard_id: int
    user_id: int
    role: str


class DashboardResponse(BaseModel):
    dashboard_name: str
    dashboard_owner: str
    tracks: list


class AddTrackRequest(BaseModel):
    dashboard_id: int
    track_id: int


class AddRoleRequest(BaseModel):
    dashboard_id: int
    role: str


class RemoveTrackRequest(BaseModel):
    dashboard_id: int
    track_id: int


class RemoveDashboardRequest(BaseModel):
    dashboard_id: int
