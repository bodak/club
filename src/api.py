from typing import Annotated

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pomelo import createLeague, listLeagues

templates = Jinja2Templates(directory="templates")
api = APIRouter()


@api.get("/")
async def home(request: Request):
    leagues = listLeagues()
    return templates.TemplateResponse(
        "index.html", {"request": request, "leagues": leagues}
    )


@api.post("/create")
async def create(league: Annotated[str, Form()]):
    createLeague(league)
    return RedirectResponse("/", status_code=303)


@api.get("/league")
async def league(id: str, request: Request):
    return templates.TemplateResponse(
        "tournament_index.html", {"request": request}
    )
