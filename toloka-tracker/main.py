from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

from fastapi.responses import HTMLResponse
from dependencies import Base, engine, Container

Base.metadata.create_all(bind=engine)

container = Container()

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return Jinja2Templates(directory="toloka_tracker/templates").TemplateResponse("index.html", {"request": request})
