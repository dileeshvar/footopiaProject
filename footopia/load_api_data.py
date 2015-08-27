from models import *
import utility
from api_helper_xmlsoccer import *
from dateutil import parser
from wiki_crawler import *
from points_calculator import *

TEAM_KEY_PREFIX = '{http://xmlsoccer.com/Team}'
TEAM_ID_KEY = TEAM_KEY_PREFIX + "Team_Id"
TEAM_NAME_KEY = TEAM_KEY_PREFIX + "Name"
TEAM_STADIUM_KEY = TEAM_KEY_PREFIX + "Stadium"
TEAM_COUNTRY_KEY = TEAM_KEY_PREFIX + "Country"
TEAM_WIKI_KEY = TEAM_KEY_PREFIX + "WIKILink"

def load_teams_tournament(tournament):
	league_name = tournament.tourn_format.tourn.tourn_name
	season = utility.convert_season_string(tournament.season)
	teams = get_teams_by_league_season(league_name, season)
	teamlist = []
	is_club = True
	if not type(teams) == list: raise Exception('Failed to load team data')
	team_cnt = 0
	for team in teams:
		if not TEAM_ID_KEY in team: continue
		team_id = team[TEAM_ID_KEY]
		team_cnt = team_cnt + 1
		if Team.objects.filter(team_api_id = team_id).count() > 0: continue
		new_team = Team()
		new_team.team_api_id = team_id
		new_team.team_cd = utility.get_team_code_from_name(team[TEAM_NAME_KEY])
		new_team.team_logo = load_logo(team[TEAM_WIKI_KEY])
		new_team.save()
		venue = Venue.add_and_get_venue(team[TEAM_STADIUM_KEY])
		if is_club:
			new_club = Club()
			new_club.club_cd = new_team
			new_club.club_name = team[TEAM_NAME_KEY]
			new_club.country = Country.add_and_get_country(team[TEAM_COUNTRY_KEY])
			new_club.home_ground = venue
			new_club.save()
			tourn_teams = TournamentTeam.objects.create(team=new_team, tourn=tournament)
	tourn_fmt = tournament.tourn_format
	if tourn_fmt.no_of_teams == 0:
		tourn_fmt.no_of_teams = team_cnt
		tourn_fmt.save()
	elif not tourn_fmt.no_of_teams == team_cnt:
		new_fmt = TournamentFormat()
		new_fmt.tourn = tourn_fmt.tourn
		new_fmt.gw_cycle_day = tourn_fmt.gw_cycle_day
		new_fmt.no_of_teams = team_cnt
		new_fmt.save()
		tournament.tourn_format = new_fmt
		tournament.save()
	# load_players(tournament)
	return tournament

FIXTURE_ID_KEY = "Id"
FIXTURE_HOMETEAM_ID_KEY = "HomeTeam_Id"
FIXTURE_AWAYTEAM_ID_KEY = "AwayTeam_Id"
FIXTURE_VENUE_KEY = "Location"
FIXTURE_GAMEWEEK_KEY = "Round"
FIXTURE_DATE_KEY = "Date"
			
def load_fixtures_tournament(tournament):
	league_name = tournament.tourn_format.tourn.tourn_name
	season = utility.convert_season_string(tournament.season)
	fixtures = get_fixtures_by_league_season(league_name, season)
	if not type(fixtures) == list: raise Exception('Failed to load fixtures')
	max_round = 0
	for fixture in fixtures:
		if not FIXTURE_ID_KEY in fixture: continue
		match_id = fixture[FIXTURE_ID_KEY]
		qs = Match.objects.filter(match_api_id = match_id)
		if qs.count() == 0:
			match = Match()
			match.match_api_id = match_id
		else:
			match = qs[0]
		match.team1 = Team.get_team_by_api_id(fixture[FIXTURE_HOMETEAM_ID_KEY])
		match.team2 = Team.get_team_by_api_id(fixture[FIXTURE_AWAYTEAM_ID_KEY])
		match.tourn = tournament
		match.match_date = parser.parse(fixture[FIXTURE_DATE_KEY])
		match.gameweek_no = int(fixture[FIXTURE_GAMEWEEK_KEY])
		match.gameweek = Gameweek.get_gameweek(tournament, fixture[FIXTURE_GAMEWEEK_KEY], add = True)
		match.venue = Venue.add_and_get_venue(fixture[FIXTURE_VENUE_KEY])
		match.save()
		if match.gameweek_no > max_round: max_round = match.gameweek_no
	tourn_fmt = tournament.tourn_format
	if tourn_fmt.no_of_gameweeks == 0:
		tourn_fmt.no_of_gameweeks = max_round
		tourn_fmt.save()
	elif not tourn_fmt.no_of_gameweeks == max_round:
		new_fmt = TournamentFormat()
		new_fmt.tourn = tourn_fmt.tourn
		new_fmt.gw_cycle_day = tourn_fmt.gw_cycle_day
		new_fmt.no_of_teams = tourn_fmt.no_of_teams
		new_fmt.no_of_gameweeks = max_round
		new_fmt.save()
		tournament.tourn_format = new_fmt
		tournament.save()
	tournament.set_date_range()
	tournament.normalize_gameweek()
	return tournament
	
RESULT_MATCH_ID = "FixtureMatch_Id"
RESULT_HOME_GOALS = "HomeGoals"
RESULT_AWAY_GOALS = "AwayGoals"

def load_results_tournament(tournament):
	league_name = tournament.tourn_format.tourn.tourn_name
	season = utility.convert_season_string(tournament.season)
	results = get_match_results_of_league(league_name, season)
	if not type(results) == list: raise Exception('Failed to load results')
	for match_result in results:
		if not RESULT_MATCH_ID in match_result: continue
		match_id = match_result[RESULT_MATCH_ID]
		match = Match.objects.filter(match_api_id = match_id)
		if len(match) != 0:
			current_match = match[0]
			current_match.team1_score = match_result[RESULT_HOME_GOALS]
			current_match.team2_score = match_result[RESULT_AWAY_GOALS]
			current_match.save()
			store_player_stats_for_the_match(current_match, match_result)
		else:
			print "Could not find appropriate match.. Skipping it"

RESULT_LIVE_MATCH_ID = "Id"
RESULT_LIVE_TIME = "Time"

# This method aids in bringing in real time updates - can be called for 30s. This brings data specific to particular tournament
def update_match_details_from_live_feed(tournament):
	league_name = tournament.tourn_format.tourn.tourn_name
	results = get_live_results(league_name)
	if not type(results) == list: raise Exception('Failed to load results')
	for match_result in results:
		if not RESULT_LIVE_MATCH_ID in match_result: continue
		if not match_result[RESULT_LIVE_TIME] == "Finished": continue
		match_id = match_result[RESULT_LIVE_MATCH_ID]
		match = Match.objects.filter(match_api_id = match_id)
		if len(match) != 0:
			current_match = match[0]
			current_match.team1_score = match_result[RESULT_HOME_GOALS]
			current_match.team2_score = match_result[RESULT_AWAY_GOALS]
			current_match.save()
			store_player_stats_for_the_match(current_match, match_result)
			update_prediction_scores_for_match(tournament, match)
		else:
			print "Could not find appropriate match.. Skipping it"

def load_results_tournament_from_last_update(tournament, lastUpdateDate, today):
	league_name = tournament.tourn_format.tourn.tourn_name
	season = utility.convert_season_string(tournament.season)
	startDate = lastUpdateDate.strftime('%Y-%m-%d')
	endDate = today.strftime('%Y-%m-%d')
	results = get_match_results_of_league_between_dates(league_name, startDate, endDate)
	if len(results) == 0: 
		return
	if not type(results) == list: raise Exception('Failed to load results')
	for match_result in results:
		if not RESULT_MATCH_ID in match_result: continue
		match_id = match_result[RESULT_MATCH_ID]
		match = Match.objects.get(match_api_id = match_id)
		match.team1_score = match_result[RESULT_HOME_GOALS]
		match.team2_score = match_result[RESULT_AWAY_GOALS]
		match.save()
		players = player.objects.filter()
		update_prediction_points_for_match(tournament, match)

RESULT_HOME_PLAYERS = ["HomeLineupGoalkeeper", "HomeLineupDefense", "HomeLineupMidfield", "HomeLineupForward"]
RESULT_HOME_SUB_PLAYERS = "HomeSubDetails"
RESULT_AWAY_PLAYERS = ["AwayLineupGoalkeeper", "AwayLineupDefense", "AwayLineupMidfield", "AwayLineupForward"]
RESULT_AWAY_SUB_PLAYERS = "AwaySubDetails"
RESULT_HOME_YELLOW_CARD_DETAILS = "HomeTeamYellowCardDetails"
RESULT_HOME_RED_CARD_DETAILS = "HomeTeamRedCardDetails"
RESULT_AWAY_YELLOW_CARD_DETAILS = "AwayTeamYellowCardDetails"
RESULT_AWAY_RED_CARD_DETAILS = "AwayTeamRedCardDetails"
RESULT_HOME_GOAL_DETAILS = "HomeGoalDetails"
RESULT_AWAY_GOAL_DETAILS = "AwayGoalDetails"
RESULT_TOTAL_MATCH_TIMING = 90
RESULT_DEFAULT_PLAYER_ID = 1110000
RESULT_DEFAULT_PLAYER_ID_LOWER = 1110000
RESULT_DEFAULT_PLAYER_ID_UPPER = 1120000

def store_player_stats_for_the_match(match, match_detail):
	home_team = match.team1
	save_player_details(match, home_team, match_detail, RESULT_HOME_PLAYERS, RESULT_HOME_SUB_PLAYERS, RESULT_HOME_YELLOW_CARD_DETAILS, RESULT_HOME_RED_CARD_DETAILS, RESULT_HOME_GOAL_DETAILS)
	away_team = match.team2
	save_player_details(match, away_team, match_detail, RESULT_AWAY_PLAYERS, RESULT_AWAY_SUB_PLAYERS, RESULT_AWAY_YELLOW_CARD_DETAILS, RESULT_AWAY_RED_CARD_DETAILS, RESULT_AWAY_GOAL_DETAILS)
	
def save_player_details(match, team, match_result, STARTING_PLAYERS, SUB_PLAYERS, YELLOW_CARD_DETAILS, RED_CARD_DETAILS, GOAL_DETAILS):
	# Can do saves if time permits
	player_timings = {}
	yellow_cards = {}
	red_cards = {}
	goal_scorers = {}
	starting_pre = "S_"
	penalty = "penalty "
	own = "Own  "
	EMPTY = "null"
	for positions in STARTING_PLAYERS:
		for players in match_result[positions].split(";"):
			if len(players) == 0: continue
			player_timings[starting_pre + players.strip()] = RESULT_TOTAL_MATCH_TIMING
			goal_scorers[players.strip()] = 0
			yellow_cards[players.strip()] = False
			red_cards[players.strip()] = False
	
	if match_result[SUB_PLAYERS] != EMPTY and match_result[SUB_PLAYERS] != None:
		for instance in match_result[SUB_PLAYERS].split(";"):
			if len(instance) == 0: continue
			time_stamp = int(instance[:instance.index("'")])
			if "': in " in instance:
				player_name = instance[instance.index(":")+4:].strip()
				goal_scorers[player_name.strip()] = 0
				yellow_cards[player_name.strip()] = False
				red_cards[player_name.strip()] = False
				player_timings[player_name] = RESULT_TOTAL_MATCH_TIMING - time_stamp
			elif "': out " in instance:
				player_name = instance[instance.index(":")+5:].strip()
				player_timings[starting_pre + player_name] = time_stamp
	if match_result[RED_CARD_DETAILS] != EMPTY and  match_result[RED_CARD_DETAILS] != None:
		noise = "&nbsp;"
		cleaned = match_result[RED_CARD_DETAILS].replace(noise, "")
		for instance in cleaned.split(";"):
			if len(instance.strip()) == 0 or ":" not in instance: continue
			red_cards[instance[instance.index(":")+2:].strip()] = True
	if match_result[YELLOW_CARD_DETAILS] != EMPTY and match_result[YELLOW_CARD_DETAILS] != None:
		noise = "&nbsp;"
		cleaned = match_result[YELLOW_CARD_DETAILS].replace(noise, "")
		for instance in cleaned.split(";"):
			if len(instance.strip()) == 0 or ":" not in instance: continue
			yellow_cards[instance[instance.index(":")+2:].strip()] = True
	if match_result[GOAL_DETAILS] != EMPTY and match_result[GOAL_DETAILS] != None:	
		for instance in match_result[GOAL_DETAILS].split(";"):
			if len(instance.strip()) == 0 or ":" not in instance: continue
			player_name = instance[instance.index(":")+1:].replace(penalty, "").strip()
			if player_name.startswith(own):
				player_name = player_name.replace(own, "").strip()
				if team == match.team1:
					oppositionTeam = match.team2 
				elif team == match.team2:
					oppositionTeam = match.team1
				oppositionPlayer = Player.get_player_from_playername_and_team(player_name, oppositionTeam)
				if len(oppositionPlayer) == 0:
					tourn = match.tourn
					myPlayers = (Player.objects.filter(player_api_id__gte=RESULT_DEFAULT_PLAYER_ID_LOWER, player_api_id__lte=RESULT_DEFAULT_PLAYER_ID_UPPER).order_by("-player_api_id"))
					if len(myPlayers) == 0:
						my_player_api_id = RESULT_DEFAULT_PLAYER_ID
					else:
						my_player_api_id = myPlayers[0].player_api_id + 1
					position = "DF"
					Player.objects.create(player_name=player_name, current_club=oppositionTeam.club, nationality=Country.add_and_get_country("Scotland"), player_type=position, player_api_id=my_player_api_id)
					Squad.objects.create(player=Player.objects.get(player_api_id=my_player_api_id), tourn_team=TournamentTeam.getTournamentTeam(tourn=tourn, team=oppositionTeam), is_active=True, current_cost=9)
					oppositionPlayer = Player.get_player_from_playername_and_team(player_name, oppositionTeam)
				details = MatchPlayerDetails.objects.filter(player=oppositionPlayer, match = match)
				if len(details) == 0:
					MatchPlayerDetails.objects.create(player = oppositionPlayer[0], match = match, team = oppositionTeam, own_goal = 1)
				else:
					player = details[0]
					player.own_goal = player.own_goal + 1
					player.save()
			else:
				goal_scorers[player_name] = goal_scorers[player_name] + 1
	for player in player_timings:
		if player.startswith(starting_pre):
			name = player[2:]
		else:
			name = player
		current_player = Player.get_player_from_playername_and_team(name, team)
		if len(current_player) == 0:
			tourn = match.tourn
			myPlayers = (Player.objects.filter(player_api_id__gte=RESULT_DEFAULT_PLAYER_ID_LOWER, player_api_id__lte=RESULT_DEFAULT_PLAYER_ID_UPPER).order_by("-player_api_id"))
			if len(myPlayers) == 0:
				my_player_api_id = RESULT_DEFAULT_PLAYER_ID
			else:
				my_player_api_id = myPlayers[0].player_api_id + 1
			position = "ST"
			Player.objects.create(player_name=name, current_club=team.club, nationality=Country.add_and_get_country("Scotland"), player_type=position, player_api_id=my_player_api_id)
			Squad.objects.create(player=Player.objects.get(player_api_id=my_player_api_id), tourn_team=TournamentTeam.getTournamentTeam(tourn=tourn, team=team), is_active=True, current_cost=9)
			current_player = Player.get_player_from_playername_and_team(name, team)
		details = MatchPlayerDetails.objects.filter(player=current_player, match = match)
		if len(details) == 0:		
			player_details = MatchPlayerDetails()
			player_details.player = current_player[0]
			if player.startswith(starting_pre):
				player_details.started = True
			else:
				player_details.started = False
			player_details.match = match
			player_details.team = team
			player_details.mins_played = player_timings[player]
			player_details.goals_scored = goal_scorers[name]
			player_details.yellow_card = yellow_cards[name]
			player_details.red_card = red_cards[name]
			player_details.points = get_player_points(player_details)
			player_details.save()
		else:
			player_details = details[0]
			if player.startswith(starting_pre):
				name = player[2:]
				player_details.started = True
			else:
				name = player
				player_details.started = False
			player_details.mins_played = player_timings[player]
			player_details.goals_scored = goal_scorers[name]
			player_details.yellow_card = yellow_cards[name]
			player_details.red_card = red_cards[name]
			player_details.points = get_player_points(player_details)
			player_details.save()

STANDING_KEY_PREFIX	= '{http://xmlsoccer.com/LeagueStanding}'
STANDING_TEAM_ID = STANDING_KEY_PREFIX + 'Team_Id'
STANDING_TEAM_PLAYED = STANDING_KEY_PREFIX + 'Played'
STANDING_TEAM_POINTS = STANDING_KEY_PREFIX + 'Points'

def load_team_standings(tournament):
	league_name = tournament.tourn_format.tourn.tourn_name
	season = utility.convert_season_string(tournament.season)
	standings = get_latest_league_standings(league_name, season)
	position = 1
	if not type(standings) == list: raise Exception('Failed to load standings')
	for team in standings:
		if not STANDING_TEAM_ID in team: continue
		team_id = team[STANDING_TEAM_ID]
		teamStanding = TeamStandings.objects.filter(tourn = tournament, team__team_api_id = team_id)
		if teamStanding.count() == 0:
			standing = TeamStandings()
			standing.tourn = tournament
			standing.team = Team.objects.get(team_api_id = team_id)
		else:
			standing = teamStanding[0]
		standing.played = team[STANDING_TEAM_PLAYED]
		standing.points = team[STANDING_TEAM_POINTS]
		standing.position = position
		standing.save()
		position = position + 1
		
PLAYERS_ID = 'Id'
PLAYERS_NAME = 'Name'
PLAYERS_TEAM_ID = 'Team_Id'
PLAYERS_POSITION = 'Position'
PLAYERS_NATIONALITY = 'Nationality'
PLAYERS_JERSEY_NUMBER = 'PlayerNumber'
PLAYERS_TYPE_MAP = {
	'Goalkeeper':'GK',
	'Defender':'DF',
	'Midfielder':'MF',
	'Forward':'ST'
}

def load_players(tourn):
	teams = Team.objects.filter(id__in=(TournamentTeam.objects.filter(tourn = tourn).values("team_id")))
	for team in teams:
		players = get_players_of_team(team.team_api_id)
		if not type(players) == list: raise Exception('Failed to load players')
		for player in players:
			if not PLAYERS_ID in player: continue
			player_api_id = player[PLAYERS_ID]
			team_id = player[PLAYERS_TEAM_ID]
			club = Club.objects.get(club_cd_id = team.id)
			name = player[PLAYERS_NAME]
			position = player[PLAYERS_POSITION]
			pos_type = PLAYERS_TYPE_MAP.get(position)
			if pos_type == None:
				continue
			nationality = player[PLAYERS_NATIONALITY]
			countryList = Country.objects.filter(country = nationality)
			if len(countryList) == 0:
				country = Country.add_and_get_country(nationality)
			else:
				country = countryList[0]
			playerObj = Player.objects.filter(player_api_id = player_api_id)
			if len(playerObj) == 0:
				Player.objects.create(player_name=name.strip(), current_club=club, nationality=country, player_type=pos_type, player_api_id=player_api_id)
				Squad.objects.create(player=Player.objects.get(player_api_id=player_api_id), tourn_team=TournamentTeam.getTournamentTeam(tourn=tourn, team=team), is_active=True, current_cost=9)


# def fetch_data_from_API():
	# load_scottish_premier_league_data();

# def createBaseUtility(country_name, tournament_name, tournament_cd, tournament_desc):
	# country = Country.add_and_get_country(country_name)
	# tourn = Tournament.objects.create(tourn_format=TournamentFormat.objects.create(tourn = TournamentBase.objects.create(tourn_cd=tournament_cd, tourn_name=tournament_name, tourn_desc = tournament_desc, country = country, tournament_type = "CL"), gw_cycle_day = "SAT"), season = "2014-15", tourn_name=tournament_name)
	# new_game = Game(tourn=tourn,game_type='F', allowed_transfers = 40, allowed_wildcards = 2)
	# new_game.save()
	# new_game = Game(tourn=tourn,game_type='P')
	# new_game.save()
	
# def load_scottish_premier_league_data():
	# tourns = "Scottish Premier League"
	# tourns_cd = "SPL"
	# tourns_desc = "Scottish League"
	# country = "Scotland"
	# season = "2014-15"
	# load_data(country, tourns, tourns_cd, tourns_desc, season)

# def load_english_premier_league_data():
	# tourns = "English Premier League"
	# tourns_cd = "EPL"
	# tourns_desc = "English League"
	# country = "England"
	# season = "2014-15"
	# load_data(country, tourns, tourns_cd, tourns_desc, season)

# def load_data(country, tourns, tourns_cd, tourns_desc, season):
	# createBaseUtility(country, tourns, tourns_cd, tourns_desc)
	# load_points_rules()
	# tourn = Tournament.getTournamentFromTournamentCode(tourns_cd, season)
	# tourn = load_teams_tournament(tourn)
	# tourn = load_fixtures_tournament(tourn)
	# load_results_tournament(tourn)
	# load_team_standings(tourn)
