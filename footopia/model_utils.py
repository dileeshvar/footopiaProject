from models import *
import datetime
from utility import *

def getGameWeek(tournament):
	date_today = datetime.datetime.today()
	isMatchThereToday = Match.objects.filter(tourn = tournament, match_date__year=date_today.year, match_date__month=date_today.month, match_date__day=date_today.day)
	if len(isMatchThereToday) > 0:
		return isMatchThereToday[0].gameweek_no
	else:
		nextMatchDay = Match.objects.filter(tourn = tournament, match_date__gt=date_today).order_by("match_date")
		if len(nextMatchDay) > 0: 
			return nextMatchDay[0].gameweek_no
		prevMatchDay = Match.objects.filter(tourn = tournament, match_date__lt=date_today).order_by("-match_date")
		return prevMatchDay[0].gameweek_no

def getPreviousGameWeek(tournament): #TODO - What if it is the first gameweek?
	current_gameweek = getGameWeek(tournament)
	return Gameweek.get_gameweek(tournament, current_gameweek - 1)

def getNextGameWeek(tournament):
	date_today = datetime.datetime.today()
	nextMatchDay = Match.objects.filter(tourn = tournament, match_date__gt=date_today).order_by("match_date")
	if len(nextMatchDay) == 0: return None
	prevMatchDay = Match.objects.filter(tourn = tournament, match_date__lt=date_today).order_by("-match_date")
	if prevMatchDay[0].gameweek_no == nextMatchDay[0].gameweek_no:
		nextGw = Match.objects.filter(tourn = tournament, gameweek_no = nextMatchDay[0].gameweek_no + 1)
		if len(nextGw) > 0:
			return nextMatchDay[0].gameweek_no + 1
		else:
			return None
	else:
		return nextMatchDay[0].gameweek_no
		
def getFixtures(tournamentCode, season, gameweek = None):
	tournament = Tournament.getTournamentFromTournamentCode(tournamentCode, season)
	if gameweek == None: gameweek = getGameWeek(tournament)
	fixtures = Match.getFixtures(tournament, gameweek)
	return fixtures

def add_prediction_to_fixtures(matches, user):
	match_with_predictions = []
	for match in matches:
		pred = match.userprediction_set.filter(user = user)
		if pred.count() > 0:
			match_with_predictions.append((match, pred))
		else:
			match_with_predictions.append((match, None))
	return match_with_predictions
	
# def load_new_results(tournament):
	# today = datetime.date.today()
	# nextMatch = Match.objects.filter(tourn=tournament, team1_score = None).order_by("match_date")[:1][0]
	# nextNearDay = nextMatch.match_date
	# load_results_tournament_from_last_update(tournament, nextNearDay, today)
	
# def getData():	
	# fetch_data_from_API()
	# create_statistics()
	
def get_team_choices_for_tourn(tourn, include_all = True):
	team_list = TournamentTeam.get_all_teams_by_tournament(tourn)
	team_choices = []
	if include_all: team_choices.append(('ALL', 'All'))
	for team in team_list:
		team_choices.append((str(team.team.id), str(team.team.club.club_name)))
	return team_choices
	
def get_team_selection_by_gw(user, tourn, gw):
	players = TeamSelection.getTeamDetails(Gameweek.get_gameweek(tourn, gw), user)
	g = 1
	m = 1
	f = 1
	d = 1
	player_info_list = {}
	edit_form_data = []

	for eachPlayer in players:
		playerPosition = eachPlayer.player.player_type
		if playerPosition == 'GK':			
			playerType = 'g' + str(g)			
			g = g + 1
		elif playerPosition == 'DF':
			playerType = 'd' + str(d)			
			d = d + 1
		elif playerPosition == 'MF':
			playerType = 'm' + str(m)
			m = m + 1
		elif playerPosition == 'ST':
			playerType = 'f' + str(f)
			f = f + 1
		
		clubName = eachPlayer.player.current_club.club_name		
		
		player_info_list[playerType] = (eachPlayer.player.id, get_player_last_name(eachPlayer.player.player_name), clubName, playerPosition, eachPlayer.price)
		edit_form_data.append({"player_out": eachPlayer.player.id, "player_in": eachPlayer.player.id})
	
	return (player_info_list, edit_form_data)

class Details(object):
	def __init__(self, player):
		self.squad_player = player
		self.minutes_played = 0
		self.goals_scored = 0
		self.yellow_cards = 0
		self.red_cards = 0
		self.own_goals = 0
		self.avg_rate_of_scoring = 0.0
		self.player_rating = 0.0
		
	def update_details(self, match_detail):
		self.minutes_played = self.minutes_played + match_detail.mins_played
		self.goals_scored = self.goals_scored + match_detail.goals_scored
		self.yellow_cards = self.yellow_cards + int(match_detail.yellow_card)
		self.red_cards = self.red_cards + int(match_detail.red_card)
		self.own_goals = self.own_goals + match_detail.own_goal
		
	def __unicode__(self):
		return self.player_name + self.team_name + self.goals_scored		

def create_statistics():
	tourns = Tournament.objects.all()
	for tournament in tourns:
		squad_players = Squad.objects.filter(tourn_team__in=(TournamentTeam.objects.filter(tourn=tournament)))
		for current_player in squad_players:
			player = current_player.player
			current_detail = Details(current_player)
			player_matches_details = MatchPlayerDetails.objects.filter(player = player, match__in=(Match.objects.filter(tourn=tournament)))
			for detail in player_matches_details:
				current_detail.update_details(detail)
			current_detail.avg_rate_of_scoring = get_avg_rate_of_scoring(current_detail)
			current_detail.player_rating = get_player_rating(current_detail)
			PlayerStatistics.add_detail_or_update(current_detail)
			
def get_avg_rate_of_scoring(current_detail):
	matches = current_detail.minutes_played/90
	if current_detail.minutes_played == 0:
		avg_rate_of_scoring = 0
	elif current_detail.minutes_played < 90:
		avg_rate_of_scoring = float(current_detail.goals_scored)
	else:
		avg_rate_of_scoring = float(current_detail.goals_scored) / float(matches)			
	return avg_rate_of_scoring

def get_player_rating(current_detail):
	# Need a way to bring in rating to GK. This can be got if matchdetails has one more column, saved which can be got by ShotsOnTarget - opponentGoals
	matches = float(current_detail.minutes_played) / float(90)
	match_rating = float(matches) / float(10)
	if current_detail.minutes_played == 0:
		yellow_rating = 0
		red_rating = 0
		own_goal_rating = 0
	elif current_detail.minutes_played < 90:
		yellow_rating = float(current_detail.yellow_cards)
		red_rating = float(current_detail.red_cards)
		own_goal_rating = float(current_detail.own_goals)
	else:
		yellow_rating = float(current_detail.yellow_cards) / float(matches)
		red_rating = float(current_detail.red_cards) / float(matches)
		own_goal_rating = float(current_detail.own_goals)/ float(matches)
	return float(10 - (yellow_rating + 2 * red_rating + 2 * own_goal_rating) + (match_rating) + (4 * current_detail.avg_rate_of_scoring))
	
def get_best_players(tournament, last_gamweek):
	return MatchPlayerDetails.get_hot_players(tournament, last_gamweek)
	
def get_best_players_in_various_positions(tournament):
	best_players = []
	gk = PlayerStatistics.objects.filter(squad__in=Squad.objects.filter(player__in=(Player.objects.filter(player_type="GK")), tourn_team__in = (TournamentTeam.objects.filter(tourn=tournament)))).order_by("-player_rating")[:1]
	df = PlayerStatistics.objects.filter(squad__in=Squad.objects.filter(player__in=(Player.objects.filter(player_type="DF")), tourn_team__in = (TournamentTeam.objects.filter(tourn=tournament)))).order_by("-player_rating")[:4]
	mf = PlayerStatistics.objects.filter(squad__in=Squad.objects.filter(player__in=(Player.objects.filter(player_type="MF")), tourn_team__in = (TournamentTeam.objects.filter(tourn=tournament)))).order_by("-player_rating")[:4]
	st = PlayerStatistics.objects.filter(squad__in=Squad.objects.filter(player__in=(Player.objects.filter(player_type="ST")), tourn_team__in = (TournamentTeam.objects.filter(tourn=tournament)))).order_by("-player_rating")[:2]
	best_players.extend(gk)
	best_players.extend(df)
	best_players.extend(mf)
	best_players.extend(st)
	return best_players
