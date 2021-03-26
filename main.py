import datetime
import requests
import json
from bs4 import BeautifulSoup
import config

output = True


class NBATeam:

    def __init__(self, team_name=None, opponent=None, is_home=None):
        self.team_name = team_name
        self.opponent = opponent
        self.is_home = is_home

    def __str__(self):
        return f'{self.team_name}'

    def __repr__(self):
        return f'{self.team_name}'

    def add_teams(self):
        todays_teams = []
        games = []
        api_url = "https://api-nba-v1.p.rapidapi.com/games/date/"  # api url
        headers = {
            'x-rapidapi-key': config.rapidAPIkey,
            'x-rapidapi-host': config.rapidAPIhost
        }

        # loop to call api twice for two different days in UTC Time. NBA games in UTC time stretch across two days.
        for x in range(2):
            # get tomorrows day
            date = datetime.datetime.now()
            day = date.day + 1

            # call api with modified date [yyyy-mm-dd]
            api_url_date = api_url + get_api_format_date(x)
            response = requests.request("GET", api_url_date, headers=headers)
            dict_response = json.loads(response.text)
            dict_game = dict_response["api"]["games"]
            games += dict_game

            # this is all due to games being played across two different days in UTC time, 6-12pm cst = 23:00-05:00 UTC.
            for game in games:
                utcTime = game["startTimeUTC"]
                utcT = int(utcTime[11:13])
                utcDate = int(utcTime[8:10])
                if utcT > 16 and x == 0:
                    home = game["hTeam"]["fullName"]
                    away = game["vTeam"]["fullName"]
                    todays_teams.append(NBATeam(home, away, is_home=True))  # Create a NBAGame object
                    todays_teams.append(NBATeam(away, home, is_home=False))
                elif utcDate == day and x == 1 and utcT <= 16:
                    home = game["hTeam"]["fullName"]
                    away = game["vTeam"]["fullName"]
                    todays_teams.append(NBATeam(home, away, is_home=True))  # Create a NBAGame object
                    todays_teams.append(NBATeam(away, home, is_home=False))

        return todays_teams


class Game:  # Game data object. Will store data about the game including a summary, betting lines(odds),
    # and injuries.

    def __init__(self, home_team, away_team):
        self.home_team = home_team
        self.away_team = away_team
        link = None
        summary = None
        odds = None
        home_injuries = None
        away_injuries = None

    def __str__(self):
        return f'{self.away_team} AT {self.home_team}'

    def __repr__(self):
        return f'{self.away_team} AT {self.home_team}'

    def create_link_str(self):  # formats the team names for the scrape
        names = [self.home_team, self.away_team]
        home_str = ""
        away_str = ""
        # link needs to have dashes in between each word. ie(san-antonio-spurs)
        for x in range(len(names)):
            name = names[x]
            name_str_arr = name.split()
            for z in range(len(name_str_arr)):
                if x == 0:
                    home_str += name_str_arr[z]
                    home_str += "-"
                elif x == 1:
                    away_str += name_str_arr[z]
                    away_str += "-"

        today_date = datetime.datetime.now()
        link_date = today_date.strftime("%y/%m/%d")  # yyyy/mm/dd
        link = f"https://sportsbookwire.usatoday.com/{link_date}/{away_str}at-{home_str}odds-picks-and-prediction/"
        newLink = link.replace("LA", "los-angeles")  # API uses LA Clippers, link needs los-angeles-clippers
        altLink = newLink[0:-1] + "-2/" # alternate version of link (i think its when a team plays a 2-game series)
        alt2Link = f"https://sportsbookwire.usatoday.com/{link_date}/{away_str}-{home_str}odds-picks-and-prediction/" # one more alternate link ive found
        links = [newLink, altLink, alt2Link]
        assigned = False

        for link in links:
            check = self.check_link(link)
            if check == 1:
                self.link = link
                assigned = True
        if not assigned:
            self.link = "0"

    def check_link(self, link):
        today_date = datetime.datetime.now()
        today_date_dash = today_date.strftime("%y-%m-%d")  # yyyy-mm-dd

        r1 = requests.get(link)
        coverpage = r1.content
        soup1 = BeautifulSoup(coverpage, 'html.parser')

        # find date
        date_search = soup1.find("meta", property="article:published_time")
        date_str = str(date_search)
        date_index = date_str.find("21")
        int_index = int(date_index)
        date = date_str[int_index:int_index + 8]

        if date == today_date_dash:
            return 1

    # Scrapes the webpage for game summary.
    def add_data(self):
        if self.link == "0":
            self.summary = "Game Not Posted Yet"
            self.odds = ""
            self.home_injuries = ""
            self.away_injuries = ""
            if output: print(self.summary)
        else:
            if output: print(self.link)
            tempString = ""
            r1 = requests.get(self.link)
            coverpage = r1.content
            soup1 = BeautifulSoup(coverpage, 'html.parser')

            coverpage_body = soup1.find_all('p')  # paragraphs
            for i in range(8):
                text = coverpage_body[i].text
                summary_str = str(text)
                if summary_str.startswith("Below"):  # don't want this paragraph
                    break
                elif summary_str.startswith("Odds"):  # don't want this paragraph
                    break
                else:  # left with what we want.
                    tempString += summary_str

            self.summary = tempString
            if output: print(self.summary)

            j = 0
            for x in range(4, 14):  # loop through divs to get the odds and injuries
                selector1 = "#content-container > div > div.articleBody > ul:nth-child("  # this is where x goes to loop thru relevant div
                selector2 = ")"
                final = selector1 + str(x) + selector2
                temp = soup1.select(final)
                if len(temp) > 0:
                    j += 1
                    if j == 1:  # betting lines
                        self.odds = temp[0].text
                        if output: print(self.odds)
                    elif j == 2:  # away injuries
                        self.away_injuries = temp[0].text
                        if output:
                            print("Away Injuries")
                            print(self.away_injuries)
                    elif j == 3:  # home injuries
                        self.home_injuries = temp[0].text
                        if output:
                            print("Home Injuries")
                            print(self.home_injuries)


# returns modified date (String)
def get_api_format_date(i):  # api returns days previous games so for current day must add 1
    now = datetime.datetime.now()
    mmyyString = now.strftime("%Y-%m-")  # YYmm
    dayInt = now.day + i
    dayString = str(dayInt)
    dateString = mmyyString + dayString
    return dateString


if __name__ == '__main__':
    game = NBATeam()  # create nba game object
    todays_teams = game.add_teams()  # add_games() adds all NBAgame objects to an array
    for team in todays_teams:
        home = ""
        away = ""
        if team.is_home:
            home = team.team_name  # str
            away = team.opponent
            a = Game(home, away)  # creates game data object
            print(a)
            a.create_link_str()  # create link for website
            a.add_data()  # creating game objects for some of tomorrows games as well?


