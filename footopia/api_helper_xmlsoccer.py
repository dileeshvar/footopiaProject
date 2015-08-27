import sys, json
from xmlsoccer.xmlsoccer import XmlSoccer

key = 'OQEMYHANHARQJCYZOOOMWNHJWFMXLHAKFJHGGSHEBPESMUOMVB'
isDemo = True

def setup():
	xmls = XmlSoccer(api_key=key, use_demo=isDemo)
	return xmls
	
def get_teams_by_league_season(leagueName, season):
	xmls = setup()
	teams = xmls.call_api(method='GetAllTeamsByLeagueAndSeason',league=leagueName, seasonDateString=season)
	return teams

def get_fixtures_by_league_season(leagueName, season):
	xmls = setup()
	fixtures = xmls.call_api(method='GetFixturesByLeagueAndSeason',league=leagueName, seasonDateString=season)
	return fixtures
	
def get_match_results_of_league(leagueName, season):
	xmls = setup()
	results = xmls.call_api(method='GetHistoricMatchesByLeagueAndSeason', league=leagueName, seasonDateString=season)
	return results

def get_match_results_of_league_between_dates(leagueName, startDate, endDate):
	xmls = setup()
	results = xmls.call_api(method='GetHistoricMatchesByLeagueAndDateInterval', league=leagueName, startDateString=startDate, endDateString = endDate)
	return results
	
def get_latest_league_standings(leagueName, season):
	xmls = setup()
	results = xmls.call_api(method='GetLeagueStandingsBySeason',league=leagueName, seasonDateString=season)
	return results
	
def get_players_of_team(teamId):
	xmls = setup()
	results = xmls.call_api(method='GetPlayersByTeam', teamId = teamId)
	return results
	
def get_live_results(leagueName):
	xmls = setup()
	results = xmls.call_api(method='GetLiveScoreByLeague',league = leagueName)
	return results