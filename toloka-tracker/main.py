from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

from fastapi.responses import HTMLResponse
from dependencies import Base, engine, Container
from toloka_tracker import auth, users, tracks, dashboards
from toloka_tracker.auth.api import auth_router
from toloka_tracker.dashboards.api import dashboards_router
from toloka_tracker.tracks.api import tracks_router
from toloka_tracker.users.api import users_router
Base.metadata.create_all(bind=engine)

container = Container()
container.wire(packages=[auth])
container.wire(packages=[users])
container.wire(packages=[tracks])
container.wire(packages=[dashboards])

app = FastAPI()
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(tracks_router)
app.include_router(dashboards_router)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return Jinja2Templates(directory="toloka_tracker/templates").TemplateResponse("index.html", {"request": request})
