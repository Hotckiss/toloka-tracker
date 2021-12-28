from pydantic import BaseModel


class Track(BaseModel):
    id: int
    name: str
    toloka_project_id: str
    max_parallel_pools: int
    min_pool_acceptance_rate: float
    max_hourly_appeals: int
    check_interval_minutes: int
    soft_alert_multiplier: float


class TrackResponse(BaseModel):
    id: int
    toloka_project_id: str
    max_parallel_pools: int
    min_pool_acceptance_rate: float
    max_hourly_appeals: int