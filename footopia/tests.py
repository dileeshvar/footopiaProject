from django.test import TestCase
from models import *
import datetime
import load_api_data
import model_utils

# Create your tests here.
class ApiTestCase(TestCase):
	def setUp(self):
		tourn_base = TournamentBase.objects.create(tourn_cd = 'SPL', tourn_name = 'Scottish Premier League', tourn_desc = 'Scottish Premier League')
		tourn_format = TournamentFormat.objects.create(tourn = tourn_base, gw_cycle_day = 'SAT')
		tourn = Tournament.objects.create(tourn_format = tourn_format, tourn_name = 'Scottish Premier League', season = '2014-15')
		
	def test_load_teams_and_fixtures(self):
		tournament = Tournament.objects.all()[0]
		load_api_data.load_teams_tournament(tournament)
		self.assertEqual(12, Club.objects.count())
		load_api_data.load_fixtures_tournament(tournament)
		self.assertEqual(33, tournament.tourn_format.no_of_gameweeks)
		self.assertEqual(198, Match.objects.count())
		load_api_data.load_results_tournament(tournament)
		self.assertTrue(len(Match.objects.all().exclude(team1_score=None)) > 0)		

class GameweekTestCase(TestCase):
	fixtures = ['data.json']
	
	def test_gameweek_no(self):
		self.assertEqual(14, model_utils.getGameWeek()) #Fix

class StandingsTestCase(TestCase):
	def setUp(self):
		tourn_base = TournamentBase.objects.create(tourn_cd = 'SPL', tourn_name = 'Scottish Premier League', tourn_desc = 'Scottish Premier League')
		tourn_format = TournamentFormat.objects.create(tourn = tourn_base, gw_cycle_day = 'SAT')
		tourn = Tournament.objects.create(tourn_format = tourn_format, tourn_name = 'Scottish Premier League', season = '2014-15')
	
	def test_standings(self):
		tournament = Tournament.objects.all()[0]
		load_api_data.load_team_standings(tournament)
		self.assertEqual(12, TeamStandings.objects.count())
