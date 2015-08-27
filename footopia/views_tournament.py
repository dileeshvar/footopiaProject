from footopia.models import *
from forms import *
import datetime
from django.http import Http404,HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from forms_change_player_price import *
from django.contrib.admin.views.decorators import staff_member_required
import tasks

def make_tournament_view(request, tournamentform, create_Tournament_Form, priceForm, getDataForm, tournaments, seasons, games):
	context = {}
	context = {'tournamentform':tournamentform, 'tournaments' : tournaments,'seasons': seasons,'games':games, 'Player_Form': priceForm,'create_Tournament_Form':create_Tournament_Form, 'Get_Data_Form':getDataForm} 
	return render(request, 'a_create_tournament.html', context)

def return_to_admin_page():
	return redirect('/admin/somerandomtexttomaketheURLlong/createTournamentBase')
	
def removeGame(request):
	return redirect('/admin/somerandomtexttomaketheURLlong/createTournamentBase')
	
@staff_member_required
def createTournament(request):
	if request.method == 'POST':
		form = CreateTournamentForm(request.POST)
		if not form.is_valid():
			tournamentform = TournamentBaseForm()
			priceForm = PlayerPriceForm()
			getDataForm = GetDataForm()
			tournaments = TournamentBase.objects.all()
			seasons = Tournament.objects.all()
			games = Game.objects.all()
			return make_tournament_view(request, tournamentform, form, priceForm, getDataForm, tournaments, seasons, games)
		season = request.POST['season']
		wildcard = request.POST['wildcard']
		transfer = request.POST['transfer']
		tournament_name = request.POST.get('tournamentname',False)
		base = TournamentBase.objects.get(tourn_name = tournament_name)
		format = TournamentFormat.objects.get(tourn=base)
		date = datetime.date.today()
		if len(Tournament.objects.filter(tourn_name=tournament_name, season=season)) > 0:
			return redirect("/admin/somerandomtexttomaketheURLlong/tournamentform")
		new_season = Tournament(tourn_format=format,tourn_name=tournament_name,season=season,start_date=date,end_date=date)
		new_season.save()
		new_game = Game(tourn=Tournament.objects.get(tourn_name=tournament_name, season=season),game_type='F',allowed_transfers=transfer,allowed_wildcards=wildcard)
		new_game.save()
		new_game = Game(tourn=Tournament.objects.get(tourn_name=tournament_name, season=season),game_type='P',allowed_transfers=0,allowed_wildcards=0)
		new_game.save()
	return return_to_admin_page()

@staff_member_required
def createTournamentBase(request):
	#entry_to_edit = get_object_or_404(Detail, user=request.user)
	if request.method == 'GET':
		tournamentform = TournamentBaseForm()
		priceForm = PlayerPriceForm()
		getDataForm = GetDataForm()
		createTournamentForm = CreateTournamentForm()
		tournaments = TournamentBase.objects.all()
		seasons = Tournament.objects.all()
		games = Game.objects.all()
		return make_tournament_view(request, tournamentform, createTournamentForm, priceForm, getDataForm, tournaments, seasons, games)
    # if method is POST, get form data to update the model
	tournamentform = TournamentBaseForm(request.POST)
	if not tournamentform.is_valid():
		priceForm = PlayerPriceForm()
		getDataForm = GetDataForm()
		createTournamentForm = CreateTournamentForm()
		tournaments = TournamentBase.objects.all()
		seasons = Tournament.objects.all()
		games = Game.objects.all()
		return make_tournament_view(request, tournamentform, createTournamentForm, priceForm, getDataForm, tournaments, seasons, games)
	tournamentform.save()
	gameweek = request.POST['game_week_cycle']
	new_tournament_format = TournamentFormat(tourn=TournamentBase.objects.get(tourn_cd=request.POST['tourn_cd']),gw_cycle_day=gameweek)
	new_tournament_format.save()
	return return_to_admin_page()
	
def find_season():
	date = datetime.date.today()
	if(date.month > 6):
		season = date.year
		nextyr = ((date.year)%100) + 1
		season = str(season) + '-' + str(nextyr)
		return season
	else:
		season = (date.year)-1
		nextyr = date.year%100
		season = str(season) + '-' + str(nextyr)
		return season
	
@staff_member_required
def get_tournament_teams(request):
	context = {}
	t = request.GET['tournament']
	tourn = get_object_or_404(Tournament, id = t)
	teams = Team.objects.filter(id__in=(TournamentTeam.objects.filter(tourn_id=tourn.id).values('team_id'))).order_by('id')
	context['teams'] = teams
	return render(request, 'req_teams.json', context, content_type='application/json')
	
@staff_member_required
def get_team_players(request):
	context = {}
	t = request.GET['team']
	team = get_object_or_404(Club, club_cd_id = t)
	players = Squad.objects.filter(player_id__in=(Player.objects.filter(current_club_id=team.club_cd_id).order_by('player_name')))
	context['players'] = players
	return render(request, 'req_players.json', context, content_type='application/json')

@staff_member_required
def change_players_price(request):
	form = PlayerPriceForm(request.POST)
	if not form.is_valid():
		tournamentform = TournamentBaseForm()
		getDataForm = GetDataForm()
		createTournamentForm = CreateTournamentForm()
		tournaments = TournamentBase.objects.all()
		seasons = Tournament.objects.all()
		games = Game.objects.all()
		context = {'tournamentform':tournamentform,'tournaments' : tournaments,'seasons': seasons,'games':games, 'Player_Form': form, 'create_Tournament_Form':createTournamentForm, 'Get_Data_Form':getDataForm}
		return make_tournament_view(request, tournamentform, createTournamentForm, form, getDataForm, tournaments, seasons, games)
	player_id = request.POST['player']
	price = request.POST['price']
	Squad.update_price(player_id, price)
	tournamentform = TournamentBaseForm()
	priceForm = PlayerPriceForm()
	getDataForm = GetDataForm()
	createTournamentForm = CreateTournamentForm()
	tournaments = TournamentBase.objects.all()
	seasons = Tournament.objects.all()
	games = Game.objects.all()
	context = {'tournamentform':tournamentform,'tournaments' : tournaments,'seasons': seasons,'games':games, 'Player_Form': priceForm,'create_Tournament_Form':createTournamentForm, 'Get_Data_Form':getDataForm}
	return render(request, 'a_create_tournament.html', context)
	
@staff_member_required
def pull_data(request):
	context={}
	tourn = request.GET['req_tourn']
	try:
		get_object_or_404(Tournament, id = tourn)
		tasks.load_tournament_data.delay(tourn)
		context['status'] = 'success'
	except:
		context['status'] = 'Fail'
	return render(request, 'status.json', context, content_type='application/json')