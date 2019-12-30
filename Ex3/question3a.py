# coding: utf-8
import rdflib
from rdflib import Literal, XSD
import urllib2
from bs4 import BeautifulSoup


# Constants
WIKI_PREFIX = "https://en.wikipedia.org"
ONTOLEGY_PREFIX = "http://example.org"
PLAYERS = "./players.txt"
GRAPH_FILE = "./graph.nt"
START_LINK = "/wiki/2016-17_Premier_League"
STR_TABLE = "table"
STR_LEAGUE = "league"
STR_CLASS = "class"
STR_PARSER = "html.parser"
STR_TITLE = "title"
STR_HREF = "href"
STR_HOME_CITY = "homeCity"
STR_COUNTRY = "country"
STR_PLAYS_FOR = "playsFor"
STR_BIRTH_PLACE = "birthPlace"
STR_BIRTH_DATE = "birthDate"
STR_POSITION = "position"
STR_LOCATED_IN = "located_in"

# Global variables
ALL_TEAMS = {}
ALL_LEAGUES = {}
ALL_PLAYERS = {}
ALL_CITIES = {}


def getUrl(url):
    for i in range(7):
        try:
            html = urllib2.urlopen("{}{}".format(WIKI_PREFIX, url))
            return html.read()
        except:
            pass
    return None


def findTeamsTable(bs):
    tables = bs.findAll(STR_TABLE, {STR_CLASS : "wikitable sortable"})
    for table in tables:
        for header in table.findAll("th"):
            h = header.text.lower().strip()
            if "stadium" == h:
                return table

    return None


def extractTeamLinks():
    page = getUrl(START_LINK)
    if page is None:
        return "Error fetching URL"

    bs = BeautifulSoup(page, STR_PARSER)
    teamsTable = findTeamsTable(bs) # Get the teams table from the initial wiki page
    if teamsTable is None:
        return "Couldn't find teams' table"

    teamLinks = {}
    for row in teamsTable.findAll("tr"):
        data = row.findAll("td")
        if len(data) > 0:
            team = data[0].find("a", href=True)
            teamLinks[team[STR_TITLE]] = (team[STR_HREF], data[1].text)

    return teamLinks


def extractPlayers(bs):
    players = []
    # Find the "span" with id containing "squad" (First-team_squad or Current_squad)
    firstTeamTable = bs.find("span", {"id" : lambda s: s and "squad" in s.lower()}).parent.find_next_sibling("table")
    tableRows = firstTeamTable.findAll("tr", {STR_CLASS : lambda s: s and s.startswith("vcard")})
    for row in tableRows:
        # Extract links to each player's wiki page (if exists)
        playerLink = row.find("span", {STR_CLASS: "fn"}).find("a", href=True)
        if playerLink:
            players.append((playerLink[STR_TITLE], playerLink[STR_HREF]))

    return players


def extractCountryOfLeague(leagueLink):
    leaguePage = getUrl(leagueLink)
    bs = BeautifulSoup(leaguePage, STR_PARSER)
    infoboxes = bs.findAll(STR_TABLE, {STR_CLASS: lambda s: s and s.startswith("infobox")})

    for infobox in infoboxes:
        try:
            headers = infobox.findAll("th")
            for h in headers:
                if STR_COUNTRY in h.text.lower():
                    data = h.find_next_sibling("td")
                    return data.find("a", href=True).text
        except:
            pass



def extractTeamAndLeagueInfo(bs, city):
    teamInfo = {STR_HOME_CITY : city}
    infoboxes = bs.findAll(STR_TABLE, {STR_CLASS : lambda s: s and s.startswith("infobox")})

    found = False
    for infobox in infoboxes:
        try:
            headers = infobox.findAll("th")
            for h in headers:
                if STR_LEAGUE in h.text.lower():
                    leagueData = h.find_next_sibling("td")
                    teamInfo[STR_LEAGUE] = leagueData.text # Extract team's current league
                    if leagueData.text not in ALL_LEAGUES:
                        # Extract leagues's country
                        ALL_LEAGUES[leagueData.text] = extractCountryOfLeague(leagueData.find("a", href=True)[STR_HREF])
                    found = True
                    break
            if found:
                break
        except:
            pass

    return teamInfo


def extractTeamInfoAndPlayers(teamPage, city):
    bs = BeautifulSoup(teamPage, STR_PARSER)
    players = extractPlayers(bs)
    teamInfo = extractTeamAndLeagueInfo(bs, city)

    return players, teamInfo


def extractCityInfo(link):
    cityPage = getUrl(link)
    if cityPage is None:
        return "Error fetching city wiki page"

    bs = BeautifulSoup(cityPage, STR_PARSER)
    infobox = bs.find(STR_TABLE, {STR_CLASS : lambda s: s and s.startswith("infobox")})

    try:
        countries = infobox.findAll("th")
        for country in countries:
            if STR_COUNTRY in country.text.lower():
                return country.find_next_sibling("td").text
    except:
        pass

    return None


def extractPlayerInfo(playerPage):
    playerInfo = {}
    bs = BeautifulSoup(playerPage, STR_PARSER)
    infobox = bs.find(STR_TABLE, {STR_CLASS : "infobox vcard"})

    try:
        # Extract info from infobox
        playerInfo[STR_BIRTH_DATE] = Literal(infobox.find("span", {STR_CLASS : "bday"}).text, datatype=XSD.date)
        playerInfo[STR_POSITION] = infobox.find("td", {STR_CLASS: "role"}).find("a").text
        playerInfo[STR_PLAYS_FOR] = infobox.find("td", {STR_CLASS: "org"}).find("a")[STR_TITLE]

        birthPlaceAnchor = infobox.find("td", {STR_CLASS: "birthplace"}).find("a", href=True)
        birthPlaceLink = birthPlaceAnchor[STR_HREF]
        birthPlaceName = birthPlaceAnchor[STR_TITLE]
        playerInfo[STR_BIRTH_PLACE] = birthPlaceName

        # Extract city info from city's wiki page
        ALL_CITIES[birthPlaceName] = extractCityInfo(birthPlaceLink)
    except:
        pass

    return playerInfo


def extractPlayersAndCitiesInfo(players):
    for player, link in players.items():
        playerPage = getUrl(link)
        if playerPage is None:
            return "Error fetching player wiki page"

        ALL_PLAYERS[player] = extractPlayerInfo(playerPage)


def extractAll():
    teamLinks = extractTeamLinks() # Extract links to team pages
    players = {}
    for team, (link, location) in teamLinks.items():
        if team in ALL_TEAMS:
            continue
        teamPage = getUrl(link)
        if teamPage is None:
            return "Error fetching team wiki page"

        city = location.split(",")[0].strip()
        p, t = extractTeamInfoAndPlayers(teamPage, city)
        players.update(dict(p))
        ALL_TEAMS[team] = t

    extractPlayersAndCitiesInfo(players)


def appendPrefix(var):
    x = var.replace(" ", "_")
    return ONTOLEGY_PREFIX + "/" + x


def rdflibTerm(var):
        return rdflib.URIRef(appendPrefix(var))


def relations(rels):
    r = {}
    for rel in rels:
        r[rel] = rdflibTerm(rel)

    return r


# Relations
RELATIONS = relations([STR_BIRTH_DATE, STR_BIRTH_PLACE, STR_COUNTRY, STR_HOME_CITY,
                       STR_LEAGUE, STR_PLAYS_FOR, STR_LOCATED_IN, STR_POSITION])


def addNodes(g, infoDict):
    for node, nodeInfo in infoDict.items():
        for rel, val in nodeInfo.items():
            if val is not None:
                g.add((rdflibTerm(node), RELATIONS[rel], rdflibTerm(val)))


def buildOntolegy():
    g = rdflib.Graph()
    extractAll() # Extract all information, and assign to above data structures.

    # Add teams
    addNodes(g, ALL_TEAMS)

    # Add players
    addNodes(g, ALL_PLAYERS)

    # Add leagues
    for league, country in ALL_LEAGUES.items():
        if country is not None:
            g.add((rdflibTerm(league), RELATIONS[STR_COUNTRY], rdflibTerm(country)))

    # Add cities
    for city, country in ALL_CITIES.items():
        if country is not None:
            g.add((rdflibTerm(city), RELATIONS[STR_LOCATED_IN], rdflibTerm(country)))

    g.serialize(GRAPH_FILE, format="nt")
    return g


if __name__ == "__main__":
    buildOntolegy()
