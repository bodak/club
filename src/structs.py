import json
import os
import time

import trueskill
from pydantic import BaseModel

data_dir = os.path.dirname("r/")

def leagues():
    return [f[:-5] for f in os.listdir(data_dir)]


class Player(BaseModel):
    rank: int
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

    @staticmethod
    def from_id(league_id):
        file_path = f"{data_dir}/{league_id}.json"
        if not os.path.exists(file_path):
            league = League(name=league_id, path=file_path)
            league.to_json()
            return league
        else:
            data = json.load(open(file_path))
            trueskill.setup(data["trueskill"], data["trueskill"] / 3)
            return League(**data)

    def to_json(self):
        json.dump(self.dict(), open(self.path, "w"), indent=2)

    def add_player(self, name):
        if name not in self.players:
            self.players[name] = Player(rank=self.trueskill)
        self.to_json()

    def delete_player(self, name):
        if name in self.players:
            del self.players[name]
        self.to_json()

    def get_players(self):
        return sorted(self.players.keys())

    def get_matches(self):
        return [(m[0], m[1], m[3], m[2], m[4]) for m in self.matches]

    def get_ranking(self):
        ranking = {"stable": [], "unstable": []}

        for name, values in self.players.items():
            if values.match_count >= self.min_games:
                ranking["stable"].append(
                    (name, values.rank, values.match_count)
                )
            else:
                ranking["unstable"].append(
                    (name, values.rank, values.match_count)
                )
        ranking["stable"] = sorted(
            ranking["stable"],
            key=lambda player: (player[1], player[2]),
            reverse=True,
        )
        ranking["unstable"] = sorted(
            ranking["unstable"],
            key=lambda player: (player[1], player[2]),
            reverse=True,
        )
        return ranking

    def add_match(self, player1, player1_score, player2, player2_score):
        now = time.localtime()
        datetime = (
            str(now[3])
            + ":"
            + str(now[4])
            + " - "
            + str(now[2])
            + "/"
            + str(now[1])
        )
        self.matches.append(
            (
                player1,
                player1_score,
                player2,
                player2_score,
                "(" + datetime + ")",
            )
        )
        self.players[player1].match_count += 1
        self.players[player2].match_count += 1

        winner, loser = (
            (player1, player2)
            if player1_score > player2_score
            else (player2, player1)
        )
        draw = player1_score == player2_score
        winner_rating, loser_rating = trueskill.rate_1vs1(
            trueskill.Rating(self.players[winner].rank),
            trueskill.Rating(self.players[loser].rank),
            drawn=draw,
        )
        self.players[winner].rank = int(winner_rating.mu)
        self.players[loser].rank = int(loser_rating.mu)
        print(winner, loser, winner_rating, loser_rating, draw)
        self.to_json()
