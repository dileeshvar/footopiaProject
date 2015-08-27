from django.shortcuts import render, get_object_or_404
from footopia.model_utils import *
from footopia.models import *
from forms_prediction import *
from forms import *
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from decorators import *
from mimetypes import guess_type

def make_tournament_view(request, tournamentCode, season, template, context):
	tour = Tournament.getTournamentFromTournamentCode(tournamentCode, season)
	context["tournament"] = tour
	context["is_pred_enrolled"] = UserEnrollment.is_enrolled(request.user.id, tour, 'P')
	context["is_foot_enrolled"] = UserEnrollment.is_enrolled(request.user.id, tour, 'F')
	context["standings"] = TeamStandings.getAll(tour)
	
	if 'gameweek' not in context:
		context['gameweek'] = getGameWeek(tour)
	return render(request, template, context)

@login_required
@tourn_code_season_validator
def displayMatch(request,tournamentCode, season):
	context = {}
	players_with_goals_teamone = []
	players_with_goals_teamtwo = []
	players_with_own_goals_teamone = []
	players_with_own_goals_teamtwo = []

	if request.method == 'GET':
		#match_id = request.GET['match_id']
		
		form = MatchInfoIdForm(request.GET)
		if not form.is_valid():
			raise Http404
		#context['match'] = Match.objects.get(match_api_id =match_id)
		match_id = form.cleaned_data.get('match_id')
		context['match'] = get_object_or_404(Match, match_api_id = match_id)
		teams = Match.getTeams(match_id)
		context['teams'] = teams
		players1 = MatchPlayerDetails.get_players_from_team(match_id,teams.team1.id)
		context['players1'] = players1
		players2 = MatchPlayerDetails.get_players_from_team(match_id,teams.team2.id)
		context['players2'] = players2
		i0 = 0
		i1 = 0
		for eachPlayer in players1:
			if eachPlayer.goals_scored > 0:
				i0 = i0 + 1
				players_with_goals_teamone.append((eachPlayer.player.player_name, eachPlayer.goals_scored))

			if eachPlayer.own_goal > 0:
				i1 = i1 + 1
				players_with_own_goals_teamone.append((eachPlayer.player.player_name, eachPlayer.own_goal))

		context['i0'] = i0
		context['i1'] = i1
		context['team1goals'] = players_with_goals_teamone
		context['team1owngoals'] = players_with_own_goals_teamone

		j0 = 0
		j1 = 0
		for eachPlayer in players2:
			if eachPlayer.goals_scored > 0:
				j0 = j0 + 1
				players_with_goals_teamtwo.append((eachPlayer.player.player_name, eachPlayer.goals_scored))

			if eachPlayer.own_goal > 0:
				j1 = j1 + 1
				players_with_own_goals_teamtwo.append((eachPlayer.player.player_name, eachPlayer.own_goal))
		context['j0'] = j0
		context['j1'] = j1
		context['team2goals'] = players_with_goals_teamtwo
		context['team2owngoals'] = players_with_own_goals_teamtwo

	return make_tournament_view(request, tournamentCode, season, 't_home_matchinfo.html', context)

@login_required
def home(request):
    context = {}
    tourn = Tournament.getCurrentTournaments()
    pred_enroll = []
    foot_enroll = []
    for tournament in tourn:
        pred_enroll.append(UserEnrollment.is_enrolled(request.user, tournament, 'P'))
        foot_enroll.append(UserEnrollment.is_enrolled(request.user, tournament, 'F'))
    context['tournaments'] = zip(tourn, foot_enroll, pred_enroll)
    return render(request, 'u_home.html', context)

@login_required
@tourn_code_season_validator
def view_tournament(request, tournamentCode, season):
	context = {}
	fixtures = getFixtures(tournamentCode, season)
	context["fixtures"] = fixtures
	return make_tournament_view(request, tournamentCode, season, 't_home.html', context)

@login_required
@tourn_code_season_validator
def get_fixtures_home(request, tournamentCode, season):
	context = {}
	form = GetFixturesForm(request.GET)
	if not form.is_valid():
		raise Http404
	gameweek = form.cleaned_data.get('gameweek')
	matchesInfo = getFixtures(tournamentCode, season, gameweek)
	context['matches'] = matchesInfo
	context['gameweek'] = gameweek
	context['now'] = datetime.datetime.now()
	return render(request, 'home_fixtures.json', context, content_type="application/json")

@login_required
def get_logos(request, teamId):
	team = get_object_or_404(Team, id = teamId)
	content_type = guess_type(team.team_logo.name)
	return HttpResponse(team.team_logo, content_type = content_type)
	
@login_required
def get_upcoming_games(request):
	context ={}
	date_today = datetime.datetime.today()
	matches = Match.objects.filter(match_date__gt=date_today).order_by("match_date")[:10]
	context['matches'] = matches
	return render(request, 'home_fixtures.json', context, content_type="application/json")