import os
import time

import trueskill
from structs import League, Player

data_dir = os.path.dirname("r/")


def importLeague(league_id):
    file_path = data_dir + "/" + str(league_id) + ".json"
    league = League.from_json(file_path)
    trueskill.setup(league.trueskill, league.trueskill / 3)
    return league


def createLeague(name):
    file_path = data_dir + "/" + name + ".json"
    l = League(name=name, path=file_path)
    if not os.path.exists(file_path):
        l.to_json()
    else:
        print("name present, change name please.\n")
        return


def addPlayer(league_id, name):
    league = importLeague(league_id)
    if name in league.players:
        return "name already in use: choose another name"

    league.players[name] = Player()
    league.to_json()
    return ""


def deletePlayer(league_id, name):
    league = importLeague(league_id)
    del league.players[name]
    league.to_json()


def addScores(league_id, player1, player1_score, player2, player2_score):
    league = importLeague(league_id)
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
    league.matches.append(
        (player1, player1_score, player2, player2_score, "(" + datetime + ")")
    )
    league.players[player1].match_count += 1
    league.players[player2].match_count += 1

    winner, loser = (
        (player1, player2)
        if player1_score > player2_score
        else (player2, player1)
    )
    draw = player1_score == player2_score
    winner_rating, loser_rating = trueskill.rate_1vs1(
        trueskill.Rating(league.players[winner].rank),
        trueskill.Rating(league.players[loser].rank),
        drawn=draw,
    )
    league.players[winner].rank = int(winner_rating.mu)
    league.players[loser].rank = int(loser_rating.mu)
    print(winner, loser, winner_rating, loser_rating, draw)
    league.to_json()


def leagueRanking(league_id):
    league = importLeague(league_id)
    ranking = {"stable": [], "unstable": []}

    for name, values in league.players.items():
        if values.match_count >= league.min_games:
            ranking["stable"].append((name, values.rank, values.match_count))
        else:
            ranking["unstable"].append((name, values.rank, values.match_count))
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


def selectPlayers(league_id):
    league = importLeague(league_id)
    return sorted(league.players.keys())


def leagueMatches(league_id):
    league = importLeague(league_id)
    matches = [(m[0], m[1], m[3], m[2], m[4]) for m in league.matches]
    return matches


def listLeagues(out="none"):
    return [f[:-5] for f in os.listdir(data_dir)]
