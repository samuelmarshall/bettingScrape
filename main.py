import datetime
import requests
import json
from bs4 import BeautifulSoup
import config

# todo add home team, and away team when printing injuries
# todo add title of home team vs away team
# todo export to txt file to email.
# todo add new comments, delete old comments

class NBAGames:
    def __init__(self, home, away):
        self.home = home
        self.away = away

    def __str__(self):
        return f'{self.home} {self.away}'

    def __repr__(self):
        return f'{self.home} {self.away}'

    def create_link(self):
        strHome = self.home
        strAway = self.away
        home_split = strHome.split()
        away_split = strAway.split()
        home_string = ""
        away_string = ""
        for x in range(len(away_split)):
            away_string += away_split[x]
            away_string += "-"

        for x in range(len(home_split)):
            home_string += home_split[x]
            home_string += "-"

        link = f"https://sportsbookwire.usatoday.com/2021/02/10/{away_string}at-{home_string}odds-picks-and-prediction/"
        newLink = link.replace("LA", "los-angeles")  # API uses LA Clippers, link needs los-angeles-clippers
        return newLink


# returns modified date (String)
def get_modified_date():  # api returns days previous games so for current day must add 1
    now = datetime.datetime.now()
    mmyyString = now.strftime("%Y-%m-") # YYmm
    dayInt = now.day + 1
    dayString = str(dayInt)
    dateString = mmyyString + dayString
    return dateString


# returns a list of links for each game to scrape
def todays_games():
    todays_games_lst = []
    todays_links = []
    url = "https://api-nba-v1.p.rapidapi.com/games/date/" # api url
    mod_url = url + get_modified_date()  # append modified date to end of url

    headers = {
        'x-rapidapi-key': config.rapidAPIkey,
        'x-rapidapi-host': config.rapidAPIhost
    }

    response = requests.request("GET", mod_url, headers=headers)
    dict_response = json.loads(response.text)  # creates dict of response.text
    games = dict_response["api"]["games"]
    for x in games:
        home = x["hTeam"]["fullName"]
        away = x["vTeam"]["fullName"]
        temp = NBAGames(home, away)
        todays_games_lst.append(temp)
    for x in range(len(todays_games_lst)):
        todays_links.append(todays_games_lst[x].create_link())

    return todays_links


# input home team and away team, outputs desc, lines, and key injuries.
def print_line_injuries(link):
    j = 0
    r1 = requests.get(link)
    coverpage = r1.content
    soup1 = BeautifulSoup(coverpage, 'html.parser')
    coverpage_body = soup1.find_all('p')  # paragraphs
    for i in range(8):
        text = coverpage_body[i].text
        teststr = str(text)
        if teststr.startswith("Below"):
            break
        elif teststr.startswith("Odds"):
            break
        else:
            print(teststr)

    for x in range(4, 14):  # todo print Home Team Name and Away Team Name in between injuries
        selector1 = "#content-container > div > div.articleBody > ul:nth-child("
        selector2 = ")"
        final = selector1 + str(x) + selector2
        temp = soup1.select(final)
        if len(temp) > 0:
            j += 1
            if j == 1:
                print("\n")
                print("Betting Lines:")
                print(temp[0].text)
            elif j == 2:
                print("Key Injuries:")
                print("Away Team")
                print(temp[0].text)
            elif j == 3:
                print("Home Team")
                print(temp[0].text)


if __name__ == '__main__':
    links = todays_games()
    for x in links:
        print_line_injuries(x)


