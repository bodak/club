import json
import math
import os
import re
import sys
import time

data_dir = os.path.dirname("r/")


def exportLeague(league):
    with open(league["path"], "w") as file_json:
        json.dump(league, file_json, indent=2)


def importLeague(league):
    file_path = data_dir + "/" + str(league) + ".json"
    with open(file_path, "r") as file_json:
        dict_league = json.load(file_json)
    return dict_league


def createLeague(name):
    file_path = data_dir + "/" + name + ".json"

    league = {
        "name": name,
        "path": file_path,
        "n_min_games": 0,
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

    data["players"][name] = {"rank": 1440, "match": 0}
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
    exportLeague(data)


def updateLeague(league, player1, player2, result):
    if result != 1 and result != 0.5 and result != 0:
        print("Wrong match result")
        return

    if player1 == player2:
        print("A player cannot play against himself")
        return

    found1 = False
    for id in range(len(league["players"])):
        if league["players"][str(id)]["name"] == player1:
            found1 = True
    if not found1:
        print("PlayerX not present in the league")
        return

    found2 = False
    for id in range(len(league["players"])):
        if league["players"][str(id)]["name"] == player2:
            found2 = True
    if not found2:
        print("PlayerY not present in the league")
        return

    else:
        [newscore1, newscore2] = addScores(league, player1, player2, result)

        for id in range(len(league["players"])):
            if league["players"][str(id)]["name"] == player1:
                league["players"][str(id)]["rank"] = newscore1
                league["players"][str(id)]["match"] = (
                    league["players"][str(id)]["match"] + 1
                )

        for id in range(len(league["players"])):
            if league["players"][str(id)]["name"] == player2:
                league["players"][str(id)]["rank"] = newscore2
                league["players"][str(id)]["match"] = (
                    league["players"][str(id)]["match"] + 1
                )

    now = time.localtime()
    dataora = (
        str(now[3])
        + ":"
        + str(now[4])
        + " - "
        + str(now[2])
        + "/"
        + str(now[1])
    )

    updateRanking(league)
    league["matches"].append((player1, player2, result, "(" + dataora + ")"))

    return exportLeague(league)


####### output


def printFormatted(league):
    omitted_characters = '"{}'
    league_formatted = json.dumps(league, indent=3, separators=("", ":\t"))

    for char in omitted_characters:
        league_formatted = league_formatted.replace(char, "")

    print(league_formatted)


def updateRanking(league):
    classification = []

    for name in league["players"].keys():
        if league["players"][name]["rank"] > 0:  # rank non negativi
            rank = league["players"][name]["rank"]
            match = league["players"][name]["match"]

            if league["players"][name]["match"] > 5:
                stabile = True

            else:
                stabile = False

            classification.append((name, rank, match, stabile))
            classification = sorted(
                classification,
                key=lambda player: (player[1], player[2]),
                reverse=True,
            )

    league["ranking"] = classification


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


def selectPlayersHtml(league):
    select = ""

    for player in selectPlayers(league):
        select += "<option value='" + player + "'>" + player + "</option>\n"

    return select


def leagueMatches(league):
    data = importLeague(league)
    matches = [(m[0], m[1], m[3], m[2], m[4]) for m in data["matches"]]
    return matches


def listLeagues(out="none"):
    return [f[:-5] for f in os.listdir(data_dir)]


# parses php input and removes any single bracket
def parse(input):
    if re.search("^[']{0,1}[A-z0-9 ]*[']{0,1}$", input):
        return (input.replace("'", ""), "argument")
    elif re.search("^'{0,1}-{1,2}[A-z]*-{0,1}[A-z]*'{0,1}$", input):
        return (input.replace("'", ""), "option")
    else:
        print("INCORRECT INPUT! Enter only alphanumeric characters and spaces")
        return


######################################################################################################################################################

HELP = "Welcome to pomelo (CLI interface), options are as follows:\n\n -l \t\t\t\t(--list) show tournament list in 'r/'\n\n - n TOURNAMENT\t\t\t(--new) to create a tournament with the given name\n TOURNAMENT -i\t\t\t(--import) to load the json file of the tournament with the given name (date /TOURNAMENTNAME/TOURNAMENTNAME.json)\n TOURNAMENT -a PLAYER \t\t(--add) add PLAYER to TOURNAMENT\n TOURNAMENT -d PLAYER\t\t(--delete) delete (reset the values of) PLAYER in TOURNAMENT\n TOURNAMENT -u G1 G2 RIS\t\t(--update) update TOURNAMENT with the RIS (result) (0, 0.5, 1) of the match between G1 and G2\n TOURNAMENT -m\t\t\t (--match) show list of TOURNAMENT matches\n TOURNAMENT -g\t\t\t(--players) show list of players in TOURNAMENT\n TOURNAMENT -p\t\t\t(--print ) show all TOURNAMENT content\n TOURNAMENT -r\t\t\t(--ranking) show TOURNAMENT ranking\n\n --help\t\t\tshow this message\n"
ERR_INPUT = "INCORRECT INPUT! Enter only alphanumeric characters and spaces\n"

######################################################################################################################################################


def main():
    if len(sys.argv) > 1:
        args = {"option": [], "arguments": []}
        for arg in sys.argv[1:]:
            parsed = parse(arg)

            if parsed[1] == "argument":
                args["arguments"].append(parsed[0])
            elif parsed[1] == "option":
                args["option"].append(parsed[0])

        if args["option"] == "-l" or args["option"] == "--list":
            listLeagues("stout")

        elif args["option"] == "-h" or args["option"] == "--help":
            print(HELP)

        else:
            if len(args["arguments"]):
                league_arg = args["arguments"][0]
                option_arg = args["option"][0]

                if option_arg == "-n" or option_arg == "--new":
                    createleague = createLeague(league_arg)
                    league = {league_arg: createleague}

                    if createleague:
                        print("league created, follow the help to populate it")

                elif option_arg == "-i" or option_arg == "--import":
                    league = importLeague(league_arg)
                    league = {league["name"]: league}

                elif option_arg == "-p" or option_arg == "--print":
                    league = importLeague(league_arg)
                    printFormatted(league)

                elif option_arg == "-a" or option_arg == "--add":
                    league = importLeague(league_arg)

                    if len(args["arguments"]) > 1:
                        player = args["arguments"][1]
                        addPlayer(league, player)
                    else:
                        print("Player name is missing!")

                elif option_arg == "-d" or option_arg == "--delete":
                    league = importLeague(league_arg)

                    if len(args["arguments"]) > 1:
                        player = args["arguments"][1]

                        deletePlayer(league, player)

                    else:
                        print("Player name is missing!")

                elif option_arg == "-u" or option_arg == "--update":
                    league = importLeague(league_arg)

                    if len(args["arguments"]) > 3:
                        player1 = args["arguments"][1]
                        player2 = args["arguments"][2]
                        outcome_match = float(
                            args["arguments"][3]
                        )  # [0, 0.5, 1]

                        updateLeague(league, player1, player2, outcome_match)

                    else:
                        print(
                            "Something is missing! Enter player1 player2 Result"
                        )

                elif option_arg == "-r" or option_arg == "--ranking":
                    league = importLeague(league_arg)

                    ranking = rankingStable(league)

                    omitted_characters = ",'[(]"
                    replaced_characters = ")"

                    if any("--html" in o for o in args["option"]):
                        pass

                    else:
                        ranking_str = " " + str(ranking["stable"])

                        if len(ranking["unstable"]):
                            ranking_str += "\n== Match < 6 ==\n " + str(
                                ranking["unstable"]
                            )

                        for char in omitted_characters:
                            ranking_str = ranking_str.replace(char, "")

                        ranking_str = ranking_str.replace(
                            replaced_characters, "\n"
                        )

                        print(ranking_str)

                elif option_arg == "-g" or option_arg == "--players":
                    league = importLeague(league_arg)

                    if any("--html" in o for o in args["option"]):
                        print(selectPlayersHtml(league))

                    else:
                        players = str(selectPlayers(league))
                        omitted_characters = "'[(])"
                        replaced_characters = ", "

                        for char in omitted_characters:
                            players = players.replace(char, "")

                        players = players.replace(replaced_characters, "\n")
                        print(players)

                elif option_arg == "-m" or option_arg == "--match":
                    league = importLeague(league_arg)
                    matches = league["matches"]

                else:
                    print(HELP)
            else:
                print("League name is missing!")
    else:
        print(HELP)


if __name__ == "__main__":
    main()
