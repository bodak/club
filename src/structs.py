import json

from pydantic import BaseModel


class Player(BaseModel):
    rank: int = 1000
    match_count: int = 0


class League(BaseModel):
    name: str
    path: str
    players: dict[str, Player] = {}
    matches: list = []
    min_games: int = 1
    trueskill: int = 1000

    @staticmethod
    def from_json(path):
        data = json.load(open(path))
        return League(**data)

    def to_json(self):
        json.dump(self.dict(), open(self.path, "w"), indent=2)
