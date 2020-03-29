import json
import re
import time
from datetime import datetime

import pandas as pd
import requests

url = "https://www.pokernow.club/games/-krRhj-L9FWLOl9i4s6dRXV3A/log"
cookie = "Cookie: _ga=GA1.2.1176765859.1584321546; npt=F7sKki9AUbSETJP6YfkMDRamCJ0SSyp0dG_aPNNpseuWt0C5_P; _gid=GA1.2.854668923.1585346561; io=nBC-yBmNIAlzApOeAJxk"


def parse(msg, players):

    r_updated = r'The admin updated the player "(.*) @ (.*)" stack from (.*) to (.*).'
    r_approved = r'The admin approved the player "(.*) @ (.*)" participation with a stack of (.*).'
    r_quits = r'The player "(.*) @ (.*)" quits the game with a stack of (.*).'

    if "The admin updated the player" in msg:
        m = re.match(r_updated, msg)
        print(msg)
        player = m.group(1)
        starting = m.group(3)
        if starting == "undefined":
            starting = 0
        else:
            starting = int(m.group(3))
        new = int(m.group(4))
        add_on = new - starting
        if player in players:
            players[player] = players[player] - add_on
        else:
            players[player] = add_on
    elif "The admin approved the player" in msg:
        m = re.match(r_approved, msg)
        player = m.group(1)
        add_on = int(m.group(3))
        if player in players:
            players[player] = players[player] - add_on
        else:
            players[player] = add_on
    elif "quits the game with a stack of" in msg:
        m = re.match(r_quits, msg)
        player = m.group(1)
        minus = int(m.group(3))
        if player in players:
            players[player] = players[player] + minus
        else:
            players[player] = + minus


def poll():
    # initial state
    with open('data/latest.json') as f:
        players = json.load(f)

    while True:
        logs = requests.get(url, headers={'Cookie': cookie})
        logs_df = pd.DataFrame(logs.json()["logs"])

        with open('data/latest.json') as f:
            latest_data = json.load(f)
            if "from" in latest_data:
                latest_date = latest_data.get("from")
            else:
                latest_date = ""

        logs_df = logs_df[logs_df["at"] > latest_date]

        msgs = logs_df["msg"]

        for msg in msgs:
            parse(msg, players)

        if latest_data != players:
            file_name = datetime.today().strftime("%Y-%d-%m__%H-%M-%S")
            players["from"] = logs_df.iloc[0]["at"]
            with open('data/%s.json' % file_name, 'w') as f:
                json.dump(players, f, ensure_ascii=False, indent=4)
            with open('data/latest.json', 'w') as f:
                json.dump(players, f, ensure_ascii=False, indent=4)

        time.sleep(5)


poll()
