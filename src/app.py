import toml
from api import api
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

project = toml.load("pyproject.toml")["project"]


def serve():
    app = FastAPI(title=project["name"], version=project["version"])
    app.mount("/static", StaticFiles(directory="static"), name="static")
    app.include_router(api)
    return app


app = serve()
