from django.shortcuts import redirect,render,get_object_or_404
from django.contrib.auth.decorators import login_required
from footopia.decorators import *
from footopia.views import *
from footopia.models import *
from footopia.utility import *

@login_required
@tourn_code_season_validator
def home(request, tournamentCode, season):
	context = {}
	tournament = Tournament.getTournamentFromTournamentCode(tournamentCode, season)
	player_stats = PlayerStatistics.get_top_scorers_utils(tournament)
	context["top_scorers"] = player_stats
	return make_tournament_view(request, tournamentCode, season, "stats_data.html", context)
	
@login_required
@tourn_code_season_validator
def get_top_scorers(request, tournamentCode, season):
	context = {}
	tournament = Tournament.getTournamentFromTournamentCode(tournamentCode, season)
	player_stats = PlayerStatistics.get_top_scorers_utils(tournament)
	context["top_scorers"] = player_stats
	return render(request, "top_scorers.json", context, content_type="application/json")
	
@login_required
@tourn_code_season_validator
def get_all_players(request, tournamentCode, season):
	context = {}
	tournament = Tournament.getTournamentFromTournamentCode(tournamentCode, season)
	player_stats = PlayerStatistics.get_all_player_utils(tournament)
	context["player_stats"] = player_stats
	return render(request, "player_details.json", context, content_type="application/json")
	
@login_required
@tourn_code_season_validator
def get_best_players_of_gameweek(request, tournamentCode, season):
	context = {}
	tournament = Tournament.getTournamentFromTournamentCode(tournamentCode, season)
	last_gamweek = getPreviousGameWeek(tournament)
	player_details = get_best_players(tournament, last_gamweek)
	context["best_players"] = player_details
	context["gameweek"] = last_gamweek.gameweek_no
	return render(request, "best_of_week.json", context, content_type="application/json")

@login_required
@tourn_code_season_validator
def get_best_team(request, tournamentCode, season):
	context = {}
	tournament = Tournament.getTournamentFromTournamentCode(tournamentCode, season)
	g = 1
	m = 1
	f = 1
	d = 1
	best_players_with_type = []
	players = get_best_players_in_various_positions(tournament)
	for eachPlayer in players:
		playerPosition = eachPlayer.squad.player.player_type
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
		clubName = eachPlayer.squad.player.current_club.club_name
		best_players_with_type.append((get_player_last_name(eachPlayer.squad.player.player_name), playerType, eachPlayer.player_rating))
	context["players_with_types"] = best_players_with_type
	return render(request, "view_best_team.json", context, content_type="application/json")