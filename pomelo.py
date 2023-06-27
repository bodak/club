#!/usr/bin/env python3

import json
import math
import os
import re
import sys
import time

data_dir = os.path.dirname("r/")


def exportLeague(league):
    with open(league["JSON_DATA"], "w") as file_json:
        json.dump(league, file_json)


def importLeague(league):
    file_path = data_dir + "/" + str(league) + "/" + str(league) + ".json"
    with open(file_path, "r") as file_json:
        dict_league = json.load(file_json)

    updateRanking(dict_league)

    return dict_league


def createLeague(name):
    dir_path = data_dir + "/" + name
    file_path = dir_path + "/" + name + ".json"
    imgs_path = dir_path + "/img"
    qr_path = imgs_path + "/qr.png"
    logo_path = imgs_path + "/logo.png"

    league = {
        "name": name,
        "FOLDER": dir_path,
        "JSON_DATA": file_path,
        "PLAYERS": {},
        "MATCHES": [],
        "RANKING": [],
        "LOGO": "",
    }

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        os.makedirs(imgs_path)

        if not os.path.exists(file_path):
            with open(file_path, "w") as fp:
                json.dump(league, fp)

            # with open(qr_path, 'w') as fp:
            # 	command = "wget -O r/" + name + "/img/qr.png 'https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=" + "http://flowin.space/pomelo/r/'" + name
            # 	os.system(command)

            # logo
            # with open(file_path, 'w') as fp:
            # 	json.dump(league, fp)

            buildHtml(name)
            buildHtml("index")

    else:
        print("name present, change name please.\n")
        return

    return league


def addPlayer(league, name):
    for id in range(len(league["PLAYERS"])):
        if league["PLAYERS"][str(id)]["name"] == name:
            print("name already in use: choose another name")
            return league

    newID = league["name"] + "_" + str(len(league["PLAYERS"]))
    newPlayer = {"name": name, "ID": newID, "RANK": 1440, "MATCH": 0}

    league["PLAYERS"][str(len(league["PLAYERS"]))] = newPlayer
    exportLeague(league)
    return league


def deletePlayer(league, name):
    for id in range(len(league["PLAYERS"])):
        if league["PLAYERS"][str(id)]["name"] == name:
            league["PLAYERS"][str(id)]["name"] = "ND"
            league["PLAYERS"][str(id)]["RANK"] = -9999
            league["PLAYERS"][str(id)]["MATCH"] = -1

    exportLeague(league)


def addScores(league, player1, player2, result):
    for id in range(len(league["PLAYERS"])):
        if league["PLAYERS"][str(id)]["name"] == player1:
            score1 = int(league["PLAYERS"][str(id)]["RANK"])
            matchX = int(league["PLAYERS"][str(id)]["MATCH"])

    for id in range(len(league["PLAYERS"])):
        if league["PLAYERS"][str(id)]["name"] == player2:
            score2 = int(league["PLAYERS"][str(id)]["RANK"])
            matchY = int(league["PLAYERS"][str(id)]["MATCH"])

    result2 = 1 - result

    expected1 = 1 / 2 + (math.atan((score1 - score2) / 200)) / math.pi
    expected2 = 1 - expected1

    if matchX > 9 and score1 > 1569:
        coefficientX = 10
    elif matchX < 6:
        coefficientX = 40
    else:
        coefficientX = 20
    if matchY > 9 and score2 > 1569:
        coefficientY = 10
    elif matchY < 6:
        coefficientY = 40
    else:
        coefficientY = 20

    partialX = round((result - expected1) * coefficientX)
    partialY = round((result2 - expected2) * coefficientY)

    score1 = score1 + partialX
    score2 = score2 + partialY

    return [score1, score2]


def updateLeague(league, player1, player2, result):
    if result != 1 and result != 0.5 and result != 0:
        print("Wrong match result")
        return

    if player1 == player2:
        print("A player cannot play against himself")
        return

    found1 = False
    for id in range(len(league["PLAYERS"])):
        if league["PLAYERS"][str(id)]["name"] == player1:
            found1 = True
    if not found1:
        print("PlayerX not present in the league")
        return

    found2 = False
    for id in range(len(league["PLAYERS"])):
        if league["PLAYERS"][str(id)]["name"] == player2:
            found2 = True
    if not found2:
        print("PlayerY not present in the league")
        return

    else:
        [newscore1, newscore2] = addScores(league, player1, player2, result)

        for id in range(len(league["PLAYERS"])):
            if league["PLAYERS"][str(id)]["name"] == player1:
                league["PLAYERS"][str(id)]["RANK"] = newscore1
                league["PLAYERS"][str(id)]["MATCH"] = (
                    league["PLAYERS"][str(id)]["MATCH"] + 1
                )

        for id in range(len(league["PLAYERS"])):
            if league["PLAYERS"][str(id)]["name"] == player2:
                league["PLAYERS"][str(id)]["RANK"] = newscore2
                league["PLAYERS"][str(id)]["MATCH"] = (
                    league["PLAYERS"][str(id)]["MATCH"] + 1
                )

    now = time.localtime()
    dataora = str(now[3]) + ":" + str(now[4]) + " - " + str(now[2]) + "/" + str(now[1])

    updateRanking(league)
    league["MATCHES"].append((player1, player2, result, "(" + dataora + ")"))

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

    for i in league["PLAYERS"]:
        if league["PLAYERS"][i]["RANK"] > 0:  # rank non negativi
            name = league["PLAYERS"][i]["name"]
            rank = league["PLAYERS"][i]["RANK"]
            match = league["PLAYERS"][i]["MATCH"]

            if league["PLAYERS"][i]["MATCH"] > 5:
                stabile = True

            else:
                stabile = False

            classification.append((name, rank, match, stabile))
            classification = sorted(
                classification, key=lambda player: (player[1], player[2]), reverse=True
            )

    league["RANKING"] = classification


def rankingStable(league):
    ranking = {"stable": [], "unstable": []}

    if league["name"] == "singolo":
        ranking["n_min_games"] = 16
    else:
        ranking["n_min_games"] = 8

    for player in league["RANKING"]:
        if player[-1]:
            ranking["stable"].append(player[0:3])
        else:
            ranking["unstable"].append(player[0:3])

    return ranking


def selectPlayers(league):
    # league = importLeague(league)
    PLAYERS = []

    for gid in league["PLAYERS"]:
        PLAYERS.append(league["PLAYERS"][gid]["name"])
        # print(gid, PLAYERS)

    PLAYERS.sort()

    return PLAYERS


def selectPlayersHtml(league):
    select = ""

    for player in selectPlayers(league):
        select += "<option value='" + player + "'>" + player + "</option>\n"

    return select


def rankingHtml(league):
    rankingTable = "<table class = 'table table-sm text-center table-bordered table-striped' ><thead class=''><tr><th scope='col'>player</th><th scope='col'>Points</th><th scope='col'>Match</th></tr></thead><tbody>\n"

    league_rank = rankingStable(league)

    for player in league_rank["stable"]:
        if league_rank["stable"].index(player) < league_rank["n_min_games"]:
            classColor = "table-success success"
        else:
            classColor = ""

        rankingTable += "<tr class='" + classColor + "'>\n"
        rankingTable += "    <td>" + str(player[0]) + "</td>\n"
        rankingTable += "    <td>" + str(player[1]) + "</td>\n"
        rankingTable += "    <td>" + str(player[2]) + "</td>\n"
        rankingTable += "</tr>\n"

    if len(league_rank["unstable"]):
        rankingunstableTable = "<table class = 'table table-sm text-center table-bordered table-striped' ><thead><tr class='bg-danger text-white'></><th scope='row'>PLAYERS out of classification</th><th></th><th></th></tr></thead><tbody>\n"

        for player in league_rank["unstable"]:
            rankingunstableTable += "<tr>\n"
            rankingunstableTable += "    <td>" + str(player[0]) + "</td>\n"
            rankingunstableTable += "    <td>" + str(player[1]) + "</td>\n"
            rankingunstableTable += "    <td>" + str(player[2]) + "</td>\n"
            rankingunstableTable += "</tr>\n"

        rankingunstableTable += "</table>\n"

        return rankingTable + rankingunstableTable


def matchHtml(league):
    match = league["MATCHES"][::-1]
    matchTable = "<table class = 'table table-sm text-center table-bordered table-striped' ><thead class=''><tr><th scope='col'>PLAYERS<th scope='col'></th><th scope='col'>Outcome</th><th scope='col'>Data</th></tr></thead><tbody>\n"

    for match in match:
        matchTable += "<tr>\n"
        matchTable += "    <td>" + str(match[0]) + "</td>\n"
        matchTable += "    <td>" + str(match[1]) + "</td>\n"
        matchTable += "    <td>" + str(2 - int(match[2])) + "</td>\n"
        matchTable += "    <td>" + str(match[3])[1:-1] + "</td>\n"
        matchTable += "</tr>\n"

    matchTable += "</table>"
    return matchTable


def buildHtml(league_in):
    if league_in == "_ALL_":
        buildHtml("index")
        for league_name in listLeagues():
            buildHtml(league_name)

    elif league_in == "index":
        index_template = open("templates/index.html", "r")
        new_index = open(f"{data_dir}/index.html", "w")
        league = listLeagues("html")

        new_index_content = index_template.read().format(LEAGUE=league)
        new_index.write(new_index_content)
        index_template.close()
        new_index.close()
    else:
        if league_in in listLeagues():
            league = importLeague(league_in)
        else:
            league = createLeague(league_in)

        match = matchHtml(league)
        ranking = rankingHtml(league)
        PLAYERS = selectPlayersHtml(league)

        index_template = open("templates/tournament_index.html", "r")
        new_index = open(league["FOLDER"] + "/" + "index.html", "w")

        if league["LOGO"] != "":
            logo_url = league["LOGO"]
        else:
            logo_url = "/pomelo/img/pomelo.png"

        new_index_content = index_template.read().format(
            LEAGUE=league["name"],
            MATCH=match,
            RANKING=ranking,
            PLAYERS=PLAYERS,
            LOGO=logo_url,
        )
        new_index.write(new_index_content)
        index_template.close()
        new_index.close()

    # T E S T
    # print(new_index_content)


def listLeagues(out="none"):
    dirs = os.listdir(data_dir)

    if out == "stout":
        for league in dirs:
            print(league)
        return

    elif out == "html":
        select = ""
        for league in sorted(dirs):
            select += "<option value='" + league + "'>" + league + "</option>\n"
        return select
    else:
        return dirs


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
                createLeague = createLeague(league_arg)
                league = {league_arg: createLeague}

                if createLeague:
                    print("league created, follow the help to populate it")

            elif option_arg == "--gen-index":
                buildHtml(league_arg)

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
                    outcome_match = float(args["arguments"][3])  # [0, 0.5, 1]

                    updateLeague(league, player1, player2, outcome_match)

                else:
                    print("Something is missing! Enter player1 player2 Result")

            elif option_arg == "-r" or option_arg == "--ranking":
                league = importLeague(league_arg)

                ranking = rankingStable(league)

                omitted_characters = ",'[(]"
                replaced_characters = ")"

                if any("--html" in o for o in args["option"]):
                    print(rankingHtml(league))

                else:
                    ranking_str = " " + str(ranking["stable"])

                    if len(ranking["unstable"]):
                        ranking_str += "\n== Match < 6 ==\n " + str(ranking["unstable"])

                    for char in omitted_characters:
                        ranking_str = ranking_str.replace(char, "")

                    ranking_str = ranking_str.replace(replaced_characters, "\n")

                    print(ranking_str)

            elif option_arg == "-g" or option_arg == "--PLAYERS":
                league = importLeague(league_arg)

                if any("--html" in o for o in args["option"]):
                    print(selectPlayersHtml(league))

                else:
                    PLAYERS = str(selectPlayers(league))
                    omitted_characters = "'[(])"
                    replaced_characters = ", "

                    for char in omitted_characters:
                        PLAYERS = PLAYERS.replace(char, "")

                    PLAYERS = PLAYERS.replace(replaced_characters, "\n")
                    print(PLAYERS)

            elif option_arg == "-m" or option_arg == "--match":
                league = importLeague(league_arg)
                matches = league["MATCHES"]

                if any("--html" in o for o in args["option"]):
                    print(matchHtml(league))

                else:
                    matches = " " + str(matches)

                    matches = matches.replace("[", "")
                    matches = matches.replace("],", "\n")
                    matches = matches.replace(", 0.0", ": 2")
                    matches = matches.replace(", 0.5", ": X")
                    matches = matches.replace(", 1.0", ": 1")
                    matches = matches.replace("1,", "1")
                    matches = matches.replace("X,", "X")
                    matches = matches.replace("2,", "2")
                    matches = matches.replace(", ", " - ")
                    # matches = matches.replace('- (', ' ')

                    omitted_characters = "[]',"
                    for char in omitted_characters:
                        matches = matches.replace(char, "")

                    print(matches)

            else:
                print(HELP)
        else:
            print("League name is missing!")
else:
    print(HELP)
