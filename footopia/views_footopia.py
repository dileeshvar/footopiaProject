from django.shortcuts import render, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from views import *
from model_utils import *
from django.core.mail import send_mail
from forms import *
from forms_footopia import *
from forms_league import *
from forms_prediction import *
from django.forms.formsets import formset_factory
import datetime, json
from django.db import transaction
from utility import *

def make_footopia_view(request, tournamentCode, season, context):
	context["my_points"] = UserEnrollment.getPoints(request.user.id, tournamentCode, season, 'F')
	context["my_rank"] = UserEnrollment.getRank(request.user.id, tournamentCode, season, 'F')
	context["leaderBoard"] = UserEnrollment.getTopUsers(tournamentCode, season, 'F')
	tourn = Tournament.getTournamentFromTournamentCode(tournamentCode, season)
	if 'gameweek' not in context:
		context['gameweek'] = getNextGameWeek(tourn)
	#TODO - Need to handle none case
	#context['lock_date'] = Gameweek.get_gameweek(tourn, context['gameweek']).lock_date
	if 'first_gw' not in context:
		context['first_gw'] = 1
	context['gw_cnt'] = context['gameweek'] - context['first_gw'] + 1
	return make_tournament_view(request, tournamentCode, season, 'f_home.html', context)

@login_required
@tourn_code_season_validator
def get_teamdetails(request, tournamentCode, season):
	context = {}
	g = 1
	m = 1
	f = 1
	d = 1
	players_with_types = []
	form = GetFixturesForm(request.GET)
	if not form.is_valid():
		raise Http404
	tourn = Tournament.getTournamentFromTournamentCode(tournamentCode, season)
	gameweek = form.cleaned_data.get('gameweek')
	players = TeamSelection.getTeamDetails(Gameweek.get_gameweek(tourn, gameweek), request.user)
	playerType = ''
	clubName = ''
	playerPosition = ''
	totalPt = ''
	gameweekPt = ''
	playerValue = ''
	userPoint = ''
	highPoint = ''
	avgPoint = ''
	userPoints = []
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
		totalPt = MatchPlayerDetails.get_total_pts_by_player_and_tourn(eachPlayer.player ,tourn)
		gameweekPt = MatchPlayerDetails.get_total_pts_by_player_and_tourn_gameweek(eachPlayer.player ,tourn, gameweek)
		playerValue = Squad.get_player_value(eachPlayer).current_cost
		players_with_types.append((get_player_last_name(eachPlayer.player.player_name), playerType, clubName, playerPosition, playerValue, gameweekPt, totalPt))
	userPoints = FootopiaPoints.get_user_gameweek_points(tourn, gameweek, request.user)

	if not userPoints.count() == 0:
		userPoint = userPoints[0].points
	else:
		userPoint = 0

	highPoint = FootopiaPoints.get_highest_point(tourn, gameweek)
	avgPoint = FootopiaPoints.get_average_point(tourn,gameweek)

	context['players_with_types'] = players_with_types
	context['gameweek'] = gameweek
	context['now'] = datetime.datetime.now()
	context['userPoint'] = userPoint
	context['highPoint'] = highPoint
	context['avgPoint'] = avgPoint

	return render(request, 'view_team.json', context, content_type="application/json")

def make_footopia_edit_view(request, template, tournamentCode, season, context):
	tourn = Tournament.getTournamentFromTournamentCode(tournamentCode, season)
	team_choices = get_team_choices_for_tourn(tourn)
	context['player_filter_form'] = PlayerFilterForm(team_choices)
	context['remaining'] = UserEnrollmentFootopia.get_transfers_and_wildcards(tourn, request.user)
	if context['gameweek'] != None:
		context['lock_date'] = Gameweek.get_gameweek(tourn, context['gameweek']).lock_date
	return make_tournament_view(request, tournamentCode, season, template, context)

@login_required
@tourn_code_season_validator
@enrollment_required('F')
def home(request, tournamentCode, season):
	tourn = Tournament.getTournamentFromTournamentCode(tournamentCode, season)
	context = {}
	context["team_exists"] = TeamSelection.team_exists(tourn, request.user)
	if context["team_exists"]:
		context['first_gw'] = TeamSelection.get_first_gw_selection(tourn, request.user)
	return make_footopia_view(request, tournamentCode, season, context)

@login_required
@tourn_code_season_validator
def join_tournament(request, tournamentCode, season):
	context = {"url_name": "join_footopia", "game_type": "Footopia"}
	tourn = Tournament.getTournamentFromTournamentCode(tournamentCode, season)
	if UserEnrollment.is_enrolled(request.user, tourn, 'F'):
		return redirect(reverse('footopia_home', args=(tournamentCode, season,)))
	if request.method == 'GET':
		context["enroll_form"] = EnrollmentForm(tourn)
		return make_tournament_view(request, tournamentCode, season, 'enroll.html', context)

	enroll_form = EnrollmentForm(tourn, request.POST)
	if not enroll_form.is_valid():
		context["enroll_form"] = enroll_form
		return make_tournament_view(request, tournamentCode, season, 'enroll.html', context)

	UserEnrollment.enroll_user(request.user, tournamentCode, season, enroll_form.cleaned_data['team'], 'F')
	context["enroll"] = 'success'
	return make_footopia_view(request, tournamentCode, season, context)

@login_required
@transaction.atomic
@tourn_code_season_validator
@enrollment_required('F')
def create_team(request, tournamentCode, season):
	context = {'mode': 'create'}
	tourn = Tournament.getTournamentFromTournamentCode(tournamentCode, season)
	if TeamSelection.team_exists(tourn, request.user):
		return redirect(reverse('footopia_home', args=(tournamentCode, season,)))
	gameweek = getNextGameWeek(tourn)
	context['gameweek'] = gameweek
	if gameweek == None: return make_tournament_view(request, tournamentCode, season, 'f_cannot_edit.html', context)
	if request.method == 'GET':
		context['create_team_form'] = CreateTeamForm()
		return make_footopia_edit_view(request, 'f_create_team.html', tournamentCode, season, context)
	create_form = CreateTeamForm(request.POST, tourn = tourn)
	if not create_form.is_valid():
		context['create_team_form'] = create_form
		return make_footopia_edit_view(request, 'f_create_team.html', tournamentCode, season, context)
	startGw = gameweek
	endGw = tourn.tourn_format.no_of_gameweeks
	keys = ['gk1', 'df1', 'df2', 'df3', 'df4', 'mf1', 'mf2', 'mf3', 'mf4', 'st1', 'st2']
	player_list = []
	for key in keys:
		player_list.append(Player.objects.get(id = create_form.cleaned_data[key]))
	TeamSelection.add_team(tourn, startGw, endGw, request.user, player_list)
	return redirect(reverse('footopia_home', args=(tournamentCode, season,)))

@login_required
@tourn_code_season_validator
@enrollment_required('F')
@transaction.atomic
def edit_team(request, tournamentCode, season):
	context = {'mode': 'edit'}
	tourn = Tournament.getTournamentFromTournamentCode(tournamentCode, season)
	if not TeamSelection.team_exists(tourn, request.user): return redirect(reverse('create_team', args=(tournamentCode, season,)))
	gameweek = getNextGameWeek(tourn)
	context['gameweek'] = gameweek
	if gameweek == None: return make_tournament_view(request, tournamentCode, season, 'f_cannot_edit.html', context)
	if request.method == 'GET':
		team_selection = get_team_selection_by_gw(request.user, tourn, gameweek)
		context['player_details'] = team_selection[0]
		context['edit_form'] = EditTeamFormSet()
		context['edit_meta_form'] = EditTeamMetaForm()
		return make_footopia_edit_view(request, 'f_edit_team.html', tournamentCode, season, context)
	edit_formset = EditTeamFormSet(request.POST, user=request.user, tourn=tourn, gw=gameweek)
	edit_meta_form = EditTeamMetaForm(request.POST, user=request.user, tourn=tourn, transfers=len(edit_formset.forms))
	if not edit_formset.is_valid() or not edit_meta_form.is_valid():
		team_selection = get_team_selection_by_gw(request.user, tourn, gameweek)
		context['player_details'] = team_selection[0]
		context['edit_form_error'] = edit_formset
		context['edit_form'] = EditTeamFormSet()
		context['edit_meta_form'] = edit_meta_form
		return make_footopia_edit_view(request, 'f_edit_team.html', tournamentCode, season, context)
	edit_player_list = []
	for form in edit_formset:
		edit_player_list.append((form.cleaned_data['player_out'], form.cleaned_data['player_in']))
	is_wildcard = edit_meta_form.cleaned_data.get('use_wildcard')
	TeamSelection.update_team(tourn, gameweek, request.user, edit_player_list, is_wildcard)
	return redirect(reverse('footopia_home', args=(tournamentCode, season,)))

@tourn_code_season_validator
def get_players(request, tournamentCode, season):
	context = {}
	tourn = Tournament.getTournamentFromTournamentCode(tournamentCode, season)
	team_choices = get_team_choices_for_tourn(tourn)
	player_filter_form = PlayerFilterForm(team_choices, request.GET)
	if not player_filter_form.is_valid():
		raise Http404
	team_filter = player_filter_form.cleaned_data.get('team')
	player_filter = player_filter_form.cleaned_data.get('player_type')
	player_list = Squad.get_player_for_team(tourn, team_filter, player_filter)
	player_list_map = []
	for squad_player in player_list:
		player_details = {}
		player_details['id'] = squad_player.player.id
		player_details['name'] = get_player_last_name(squad_player.player.player_name)
		player_details['team_cd'] = squad_player.tourn_team.team.team_cd
		player_details['team_name'] = squad_player.tourn_team.team.club.club_name
		player_details['cost'] = str(squad_player.current_cost)
		player_details['type'] = squad_player.player.player_type
		player_details['pts'] = MatchPlayerDetails.get_total_pts_by_player_and_tourn(squad_player.player, tourn)
		player_list_map.append(player_details)
	return HttpResponse(json.dumps(player_list_map), content_type='application/json')

@login_required
@tourn_code_season_validator
@enrollment_required('F')
def get_my_leagues(request, tournamentCode, season):
	context = {}
	context['league_type'] = "f_get_my_leagues"
	context['league_create'] = "f_create_new_league"
	context['league_join'] = "f_join_league"
	context['league_view'] = "f_view_league"
	context['league_data'] = GameLeague.getUserGameLeague(request.user, tournamentCode, season, 'F')
	return make_tournament_view(request, tournamentCode, season, 'league_home.html', context)

@login_required
@transaction.atomic
@tourn_code_season_validator
@enrollment_required('F')
def create_new_league(request, tournamentCode, season):
	context = {}
	context['league_type'] = "f_get_my_leagues"
	context['league_create'] = "f_create_new_league"
	context['league_join'] = "f_join_league"
	context['league_view'] = "f_view_league"
	if request.method == "GET":
		context['L_form'] = CreateLeagueForm()
		return make_tournament_view(request, tournamentCode, season, 'league_create.html', context)
	form = CreateLeagueForm(request.POST)
	context['L_form'] = form
	if not form.is_valid():
		return make_tournament_view(request, tournamentCode, season, 'league_create.html', context)
	gameweek_no = getNextGameWeek(Tournament.getTournamentFromTournamentCode(tournamentCode, season))
	uniqcode = GameLeague.createLeague(request.user, tournamentCode, season, 'F', form.cleaned_data['name'], form.cleaned_data['description'], Gameweek.objects.get(tourn = Tournament.getTournamentFromTournamentCode(tournamentCode, season), gameweek_no = gameweek_no))
	email_body = """
	Hi there,
	"""+request.user.username+""" has invited you to join his/her Footopia league """+form.cleaned_data['name']+"""
	Click the below link and enter this uniquecode """+uniqcode+""" and be a part of this awesome league
	http://%s%s
	""" % (request.get_host(),
		reverse('f_join_league', args=(tournamentCode, season)))
	send_mail(subject="Invitation: Join my Footopia League - "+form.cleaned_data['name'],
		message= email_body,
		from_email= request.user.email,
		recipient_list= form.cleaned_data['email_ids'])
	return get_my_leagues(request, tournamentCode, season)


@login_required
@transaction.atomic
@tourn_code_season_validator
@enrollment_required('F')
def join_league(request, tournamentCode, season):
	context = {}
	context['league_type'] = "f_get_my_leagues"
	context['league_create'] = "f_create_new_league"
	context['league_join'] = "f_join_league"
	context['league_view'] = "f_view_league"
	if request.method == "GET":
		context['J_form'] = JoinLeagueForm()
		return make_tournament_view(request, tournamentCode, season, 'league_join.html', context)
	form = JoinLeagueForm(request.POST, user = request.user, tourn = tournamentCode, gt = 'F', season = season)
	context['J_form'] = form
	if not form.is_valid():
		return make_tournament_view(request, tournamentCode, season, 'league_join.html', context)
	GameLeague.addUser(request.user, form.cleaned_data['uniquecode'])
	return get_my_leagues(request, tournamentCode, season)

@login_required
@transaction.atomic
@tourn_code_season_validator
@enrollment_required('F')
@league_join_required('F')
def view_league(request, tournamentCode, season, leagueId):
	context = {}
	context['league_type'] = "f_get_my_leagues"
	context['league_create'] = "f_create_new_league"
	context['league_join'] = "f_join_league"
	context['league_view'] = "f_view_league"
	current = getGameWeek(Tournament.getTournamentFromTournamentCode(tournamentCode, season))
	context['leader_data'] = GameLeague.getFootopiaScore(leagueId, current, tournamentCode, season)
	return make_tournament_view(request, tournamentCode, season, 'league_view.html', context)
	
@login_required
@transaction.atomic
@tourn_code_season_validator
def rules(request,tournamentCode,season):
	context = {}
	tourn = Tournament.getTournamentFromTournamentCode(tournamentCode,season)
	game = tourn.game_set.get(game_type="F")
	context["allowed_transfers"] = game.allowed_transfers
	context["wildcard"] = game.allowed_wildcards
	return make_tournament_view(request,tournamentCode,season,'f_rules.html',context)
