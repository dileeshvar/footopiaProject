from django.shortcuts import render, get_object_or_404
from django.http import Http404
from views import *
from model_utils import *
from forms import *
from forms_prediction import *
from forms_league import *
from django.forms.formsets import formset_factory
import datetime, pytz
from django.db import transaction
from django.core.mail import send_mail
from django.core.urlresolvers import reverse

def make_prediction_view(request, tournamentCode, season, context):
	PredictionFormSet = formset_factory(PredictionForm)
	context["my_points"] = UserEnrollment.getPoints(request.user.id, tournamentCode, season)
	context["my_rank"] = UserEnrollment.getRank(request.user.id, tournamentCode, season)
	context["leaderBoard"] = UserEnrollment.getTopUsers(tournamentCode, season, 'P')
	if 'gameweek' not in context:
		context['gameweek'] = getGameWeek(Tournament.getTournamentFromTournamentCode(tournamentCode, season))
	if 'formset' not in context:
		context['formset'] = PredictionFormSet()
	return make_tournament_view(request, tournamentCode, season, 'p_home.html', context)

@login_required
@tourn_code_season_validator
@enrollment_required('P')
def home(request, tournamentCode, season):
	context = {}
	return make_prediction_view(request, tournamentCode, season, context)

@login_required
@tourn_code_season_validator
def get_fixtures(request, tournamentCode, season):
	context = {}
	form = GetFixturesForm(request.GET)
	if not form.is_valid():
		raise Http404
	gameweek = form.cleaned_data.get('gameweek')
	matches = getFixtures(tournamentCode, season, gameweek)
	context['matches_with_pred'] = add_prediction_to_fixtures(matches, request.user)
	context['gameweek'] = gameweek
	context['now'] = datetime.datetime.now(pytz.UTC)
	return render(request, 'pred_fixtures.json', context, content_type="application/json")

@login_required
@transaction.atomic
@tourn_code_season_validator
@enrollment_required('P')
def predict(request, tournamentCode, season):
	context = {}
	gw_form = GetFixturesForm(request.POST)
	PredictionFormSet = formset_factory(PredictionForm)
	pred_formset = PredictionFormSet(request.POST)
	now = datetime.datetime.now(pytz.utc)
	if gw_form.is_valid():
		context['gameweek'] = gw_form.cleaned_data.get('gameweek')
		if pred_formset.is_valid():
			for form in pred_formset:
				m = get_object_or_404(Match, match_api_id = form.cleaned_data['match'])
				if m.match_date < now or form.cleaned_data['team1_score'] == None:
					continue
				UserPrediction.add_or_update_prediction(request.user, m, form.cleaned_data['team1_score'], form.cleaned_data['team2_score'])
			return make_prediction_view(request, tournamentCode, season, context)
		else:
			context['dataerror'] = True
			context['formset'] = pred_formset
			return make_prediction_view(request, tournamentCode, season, context)
	else:
		context['error'] = True
		return make_prediction_view(request, tournamentCode, season, context)

@login_required
@tourn_code_season_validator
def join_tournament(request, tournamentCode, season):
	context = {"url_name": "join_prediction", "game_type": "Prediction"}
	tourn = Tournament.getTournamentFromTournamentCode(tournamentCode, season)
	if UserEnrollment.is_enrolled(request.user, tourn, 'P'):
		return redirect(reverse('predict_home', args=(tournamentCode, season,)))
	if request.method == 'GET':
		context["enroll_form"] = EnrollmentForm(tourn)
		return make_tournament_view(request, tournamentCode, season, 'enroll.html', context)

	enroll_form = EnrollmentForm(tourn, request.POST)
	if not enroll_form.is_valid():
		context["enroll_form"] = enroll_form
		return make_tournament_view(request, tournamentCode, season, 'enroll.html', context)

	UserEnrollment.enroll_user(request.user, tournamentCode, season, enroll_form.cleaned_data['team'], 'P')
	context["enroll"] = 'success'
	return make_prediction_view(request, tournamentCode, season, context)

@login_required
@tourn_code_season_validator
@enrollment_required('P')
def get_my_leagues(request, tournamentCode, season):
	context = {}
	context['league_type'] = "p_get_my_leagues"
	context['league_create'] = "p_create_new_league"
	context['league_join'] = "p_join_league"
	context['league_view'] = "p_view_league"
	context['league_data'] = GameLeague.getUserGameLeague(request.user, tournamentCode, season, 'P')
	return make_tournament_view(request, tournamentCode, season, 'league_home.html', context)

@login_required
@transaction.atomic
@tourn_code_season_validator
@enrollment_required('P')
def create_new_league(request, tournamentCode, season):
	context = {}
	context['league_type'] = "p_get_my_leagues"
	context['league_create'] = "p_create_new_league"
	context['league_join'] = "p_join_league"
	context['league_view'] = "p_view_league"
	if request.method == "GET":
		context['L_form'] = CreateLeagueForm()
		return make_tournament_view(request, tournamentCode, season, 'league_create.html', context)
	form = CreateLeagueForm(request.POST)
	context['L_form'] = form
	if not form.is_valid():
		return make_tournament_view(request, tournamentCode, season, 'league_create.html', context)
	gameweek_no = getNextGameWeek(Tournament.getTournamentFromTournamentCode(tournamentCode, season))
	uniqcode = GameLeague.createLeague(request.user, tournamentCode, season, 'P', form.cleaned_data['name'], form.cleaned_data['description'], Gameweek.objects.get(tourn = Tournament.getTournamentFromTournamentCode(tournamentCode, season), gameweek_no = gameweek_no))
	email_body = """
	Hi there,
	"""+request.user.username+""" has invited you to join his/her prediction league """+form.cleaned_data['name']+"""
	Click the below link and enter this uniquecode """+uniqcode+""" and be a part of this awesome league
	http://%s%s
	""" % (request.get_host(),
		reverse('p_join_league', args=(tournamentCode, season)))
	send_mail(subject="Invitation: Join my Prediction League - "+form.cleaned_data['name'],
		message= email_body,
		from_email= request.user.email,
		recipient_list= form.cleaned_data['email_ids'])
	return get_my_leagues(request, tournamentCode, season)

@login_required
@transaction.atomic
@tourn_code_season_validator
@enrollment_required('P')
def join_league(request, tournamentCode, season):
	context = {}
	context['league_type'] = "p_get_my_leagues"
	context['league_create'] = "p_create_new_league"
	context['league_join'] = "p_join_league"
	context['league_view'] = "p_view_league"
	if request.method == "GET":
		context['J_form'] = JoinLeagueForm()
		return make_tournament_view(request, tournamentCode, season, 'league_join.html', context)
	form = JoinLeagueForm(request.POST, user = request.user, tourn = tournamentCode, gt = 'P', season = season)
	context['J_form'] = form
	if not form.is_valid():
		return make_tournament_view(request, tournamentCode, season, 'league_join.html', context)
	GameLeague.addUser(request.user, form.cleaned_data['uniquecode'])
	return get_my_leagues(request, tournamentCode, season)

@login_required
@transaction.atomic
@tourn_code_season_validator
@enrollment_required('P')
@league_join_required('P')
def view_league(request, tournamentCode, season, leagueId):
	context = {}
	context['league_type'] = "p_get_my_leagues"
	context['league_create'] = "p_create_new_league"
	context['league_join'] = "p_join_league"
	context['league_view'] = "p_view_league"
	current = getGameWeek(Tournament.getTournamentFromTournamentCode(tournamentCode, season))
	context['leader_data'] = GameLeague.getPredictionScore(leagueId, current, tournamentCode, season)
	return make_tournament_view(request, tournamentCode, season, 'league_view.html', context)

@login_required
@transaction.atomic
@tourn_code_season_validator
def rules(request, tournamentCode, season):
	context = {}
	return make_tournament_view(request,tournamentCode,season,'p_rules.html',context)