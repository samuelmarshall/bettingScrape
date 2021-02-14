import datetime
import requests
import json
from bs4 import BeautifulSoup
import config
from EmailClient import send_email

# todo add error validation, maybe check that all links are live before scraping them?
# todo add new comments, delete old comments
email_aggregate = []


class NBAGames:
    def __init__(self, home, away):
        self.home = home
        self.away = away

    def __str__(self):
        return f'{self.away} AT {self.home}'

    def __repr__(self):
        return f'{self.home} {self.away}'

    def create_link(self):
        today_date = datetime.datetime.now()
        mmyyddString = today_date.strftime("%y/%m/%d")  # yymmdd
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

        link = f"https://sportsbookwire.usatoday.com/{mmyyddString}/{away_string}at-{home_string}odds-picks-and-prediction/"
        newLink = link.replace("LA", "los-angeles")  # API uses LA Clippers, link needs los-angeles-clippers
        return newLink

    def print_home(self):
        home = self.home
        print(home)  # print is for console output, return is used to aggregate info into email_aggregate[] for email
        return home

    def print_away(self):
        away = self.away
        print(away)
        return away

    def print_title(self):
        home = self.home
        away = self.away
        temp = away + " AT " + home
        print(temp)
        email_aggregate.append(temp)


# returns modified date (String)
def get_modified_date():  # api returns days previous games so for current day must add 1
    now = datetime.datetime.now()
    mmyyString = now.strftime("%Y-%m-") # YYmm
    dayInt = now.day + 1
    dayString = str(dayInt)
    dateString = mmyyString + dayString
    return dateString


# returns a list of games
def todays_games():
    todays_games_lst = []
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

    return todays_games_lst


# input home team and away team, outputs desc, lines, and key injuries.
def print_line_injuries(link, game):
    j = 0
    tempString = ""
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
            tempString += teststr
    email_aggregate.append(tempString)

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
                # email_aggregate.append("Betting Lines: ")
                print(temp[0].text)
                email_aggregate.append("Betting Lines: " + temp[0].text)
            elif j == 2:
                print("Key Injuries:")
                email_aggregate.append("Key Injuries:")
                tt = game.print_away()
                print(temp[0].text)
                email_aggregate.append(tt + ":  " + temp[0].text)
            elif j == 3:
                rr = game.print_home()
                print(temp[0].text)
                email_aggregate.append(rr + ":  " + temp[0].text)


def get_todays_links(games):
    todays_links = []
    for x in range(len(games)):
        todays_links.append(games[x].create_link())
    return todays_links


if __name__ == '__main__':
    games_lst = todays_games()   # returns list of todays games
    links = get_todays_links(games_lst)  # returns links to scrape for todays games
    i = 0
    for x in links:
        games_lst[i].print_title()
        print(x)
        print("")
        print_line_injuries(x, games_lst[i])
        print("---------------------------------------------------------")
        email_aggregate.append("--------------------------------------------------------------------------------------")
        i += 1
    # send_email(email_aggregate)



