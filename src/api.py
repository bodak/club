from typing import Annotated

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from structs import League, leagues

templates = Jinja2Templates(directory="templates")
api = APIRouter()


@api.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "leagues": leagues()}
    )


@api.post("/create")
async def create(league_id: Annotated[str, Form()]):
    League.from_id(league_id)
    return RedirectResponse("/", status_code=303)


@api.get("/league")
async def league(league_id: str):
    return RedirectResponse(f"/{league_id}", status_code=303)


@api.get("/{league_id}")
async def get_league(request: Request, league_id: str):
    league = League.from_id(league_id)
    return templates.TemplateResponse(
        "tournament_index.html",
        {
            "request": request,
            "league": league_id,
            "players": league.get_players(),
            "matches": league.get_matches(),
            "ranking": league.get_ranking(),
        },
    )


@api.post("/{league_id}/player")
async def add_player(league_id: str, player: Annotated[str, Form()]):
    league = League.from_id(league_id)
    league.add_player(name=player)
    return RedirectResponse(f"/{league_id}", status_code=303)


@api.post("/{league_id}/delete_player")
async def delete_player(league_id: str, player: Annotated[str, Form()]):
    league = League.from_id(league_id)
    league.delete_player(name=player)
    return RedirectResponse(f"/{league_id}", status_code=303)


@api.post("/{league_id}/score")
async def score(
    league_id: str,
    player1: Annotated[str, Form()],
    player1_score: Annotated[int, Form()],
    player2: Annotated[str, Form()],
    player2_score: Annotated[int, Form()],
):
    league = League.from_id(league_id)
    league.add_match(player1, player1_score, player2, player2_score)
    return RedirectResponse(f"/{league_id}", status_code=303)
