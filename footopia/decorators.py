from models import *
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.core.urlresolvers import reverse

def tourn_code_season_validator(func):
	def checker(request, tournamentCode, season, *args, **kwargs):
		try:
			tourn = Tournament.getTournamentFromTournamentCode(tournamentCode, season)
		except ObjectDoesNotExist:
			raise Http404
		return func(request, tournamentCode, season, *args, **kwargs)
	return checker

def enrollment_required(game_type):
	def wrap(func):
		def checker(request, tournamentCode, season, *args, **kwargs):
			tourn = Tournament.getTournamentFromTournamentCode(tournamentCode, season)
			if UserEnrollment.is_enrolled(request.user, tourn, game_type):
				return func(request, tournamentCode, season, *args, **kwargs)
			else:
				url_name = 'join_footopia' if game_type == 'F' else 'join_prediction'
				return redirect(reverse(url_name, args=(tournamentCode, season,)))
		return checker
	return wrap

def league_join_required(game_type):
	def wrap(func):
		def checker(request, tournamentCode, season, leagueId, *args, **kwargs):
			tourn = Tournament.getTournamentFromTournamentCode(tournamentCode, season)
			game = Game.objects.get(tourn = tourn, game_type = game_type)
			try:
				GameLeague.objects.get(Q(user = request.user)| Q(users__id = request.user.id), game = game, id = leagueId)
				return func(request, tournamentCode, season, leagueId, *args, **kwargs)
			except GameLeague.DoesNotExist:
				url_name = 'p_join_league' if game_type == 'F' else 'f_join_league'
				return redirect(reverse(url_name, args=(tournamentCode, season,)))
		return checker
	return wrap
