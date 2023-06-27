import json
import math
import os
import re
import sys
import time

import trueskill

data_dir = os.path.dirname("r/")


def exportLeague(league):
    with open(league["path"], "w") as file_json:
        json.dump(league, file_json, indent=2)


def importLeague(league):
    file_path = data_dir + "/" + str(league) + ".json"
    with open(file_path, "r") as file_json:
        data = json.load(file_json)
    trueskill.setup(data["trueskill_mu"], data["trueskill_mu"] / 3)
    return data


def createLeague(name):
    file_path = data_dir + "/" + name + ".json"

    league = {
        "name": name,
        "path": file_path,
        "n_min_games": 0,
        "trueskill_mu": 1000,
        "players": {},
        "matches": [],
        "logo": "",
    }

    if not os.path.exists(file_path):
        with open(file_path, "w") as fp:
            json.dump(league, fp)
    else:
        print("name present, change name please.\n")
        return
    return league


def addPlayer(league, name):
    data = importLeague(league)
    if name in data["players"]:
        return "name already in use: choose another name"

    data["players"][name] = {"rank": int(trueskill.Rating().mu), "match": 0}
    exportLeague(data)
    return ""


def deletePlayer(league, name):
    data = importLeague(league)
    del data["players"][name]
    exportLeague(data)


def addScores(league, player1, player1_score, player2, player2_score):
    data = importLeague(league)
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
    data["matches"].append(
        (player1, player1_score, player2, player2_score, "(" + datetime + ")")
    )
    data["players"][player1]["match"] += 1
    data["players"][player2]["match"] += 1

    winner, loser = (
        (player1, player2)
        if player1_score > player2_score
        else (player2, player1)
    )
    draw = player1_score == player2_score
    winner_rating, loser_rating = trueskill.rate_1vs1(
        trueskill.Rating(data["players"][winner]["rank"]),
        trueskill.Rating(data["players"][loser]["rank"]),
        drawn=draw,
    )
    data["players"][winner]["rank"] = int(winner_rating.mu)
    data["players"][loser]["rank"] = int(loser_rating.mu)
    print(winner, loser, winner_rating, loser_rating, draw)
    exportLeague(data)


def leagueRanking(league):
    data = importLeague(league)
    ranking = {"stable": [], "unstable": []}

    for name, values in data["players"].items():
        if values["match"] >= data["n_min_games"]:
            ranking["stable"].append((name, values["rank"], values["match"]))
        else:
            ranking["unstable"].append((name, values["rank"], values["match"]))
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


def selectPlayers(league):
    data = importLeague(league)
    return sorted(data["players"].keys())


def leagueMatches(league):
    data = importLeague(league)
    matches = [(m[0], m[1], m[3], m[2], m[4]) for m in data["matches"]]
    return matches


def listLeagues(out="none"):
    return [f[:-5] for f in os.listdir(data_dir)]
