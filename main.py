from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from database import create_tables, engine
from routers.api import (
    admin as admin_router,
)

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield
    await engine.dispose()
app = FastAPI(lifespan=lifespan)


app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


app.include_router(admin_router.router)


def main():
    print("Hello from codeatlas!")


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})
