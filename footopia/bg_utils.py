from load_api_data import *
from models import *

# This method loads tournament data. This is just called once when the tournament is created or when the admin requests for updating tournament data
def load_tournament_data(tourn):
	tourn = load_teams_tournament(tourn)
	load_players(tourn)
	tourn = load_fixtures_tournament(tourn)
	load_results_tournament(tourn)
	load_team_standings(tourn)
	create_statistics()

# This method refreshes the players, fixtures and standings of the current tournament. This should be called periodically (once a week)
def refresh_tournament(tourn):
	tourn = load_fixtures_tournament(tourn)
	load_players(tourn)

# This method loads new results for a tournament. This should be called periodically (every 1 hr)
def refresh_results(tourn):
	today = datetime.datetime.now(pytz.utc)
	nextMatch = Match.objects.filter(tourn=tourn, team1_score = None).order_by("match_date")[:1]
	if nextMatch.count() == 0: return #If no matches in future
	nextMatchDate = nextMatch[0].match_date
	if today.date() > nextMatchDate.date(): return #If no matches today
	update_match_details_from_live_feed(tourn)
	load_team_standings(tourn)
	#Need to update footopia points and statistics
	calculate_footopia_points_for_tournament(tourn)
	create_statistics()
