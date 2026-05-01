from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from database import Base, engine
from routers import auth as auth_router
from routers import dashboard, projects, tasks


app = FastAPI(title="Team Task Manager")
templates = Jinja2Templates(directory="templates")
app.state.templates = templates


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return RedirectResponse("/dashboard")


app.include_router(auth_router.router)
app.include_router(dashboard.router)
app.include_router(projects.router)
app.include_router(tasks.router)
