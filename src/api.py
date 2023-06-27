from typing import Annotated

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pomelo import (
    addPlayer,
    addScores,
    createLeague,
    deletePlayer,
    leagueMatches,
    leagueRanking,
    listLeagues,
    selectPlayers,
)

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
async def select_league(id: str):
    return RedirectResponse(f"/{id}", status_code=303)


@api.get("/{league_id}")
async def league_get(request: Request, league_id: str):
    players = selectPlayers(league_id)
    ranking = leagueRanking(league_id)
    matches = leagueMatches(league_id)
    return templates.TemplateResponse(
        "tournament_index.html",
        {
            "request": request,
            "league": league_id,
            "players": players,
            "matches": matches,
            "ranking_stable": ranking["stable"],
            "ranking_unstable": ranking["unstable"],
        },
    )


@api.post("/{league_id}/player")
async def add_player(league_id: str, player: Annotated[str, Form()]):
    addPlayer(league=league_id, name=player)
    return RedirectResponse(f"/{league_id}", status_code=303)


@api.post("/{league_id}/delete_player")
async def delete_player(league_id: str, player: Annotated[str, Form()]):
    deletePlayer(league=league_id, name=player)
    return RedirectResponse(f"/{league_id}", status_code=303)


@api.post("/{league_id}/score")
async def score(
    league_id: str,
    player1: Annotated[str, Form()],
    player1_score: Annotated[int, Form()],
    player2: Annotated[str, Form()],
    player2_score: Annotated[int, Form()],
):
    addScores(league_id, player1, player1_score, player2, player2_score)
    return RedirectResponse(f"/{league_id}", status_code=303)
