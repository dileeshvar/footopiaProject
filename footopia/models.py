from django.db import models
from django.db.models import Min, Max, Sum, Avg

from django.contrib.auth.models import User
from django.db import transaction
import datetime, pytz
import utility
from django.db.models import Q

class Team(models.Model):
	team_cd = models.CharField(max_length = 3)
	team_api_id = models.IntegerField(null=True, blank=True)
	team_logo = models.ImageField(upload_to="team_logos/", default="team_logos/None/no-img.PNG", blank = True)

	@staticmethod
	def get_team_by_api_id(api_id):
		return Team.objects.get(team_api_id = api_id)

class Country(models.Model):
	country_cd = models.OneToOneField(Team, primary_key=True)
	country = models.CharField(max_length = 45)

	@staticmethod
	def add_and_get_country(country):
		if Country.objects.filter(country = country).count() == 0:
			team = Team()
			team.team_cd = utility.get_team_code_from_name(country)
			team.save()
			new_country = Country()
			new_country.country_cd = team
			new_country.country = country
			new_country.save()
		return Country.objects.get(country = country)

	def __unicode__(self):
		return u'{0}'.format(self.country)

class Venue(models.Model):
	venue_name = models.CharField(max_length = 30)
	capacity = models.IntegerField(null=True, blank=True)

	@staticmethod
	def add_and_get_venue(venue_name, capacity = None):
		if Venue.objects.filter(venue_name = venue_name).count() == 0:
			new_venue = Venue()
			new_venue.venue_name = venue_name
			new_venue.capacity = capacity
			new_venue.save()
		return Venue.objects.get(venue_name = venue_name)

class Club(models.Model):
	club_cd = models.OneToOneField(Team, primary_key=True)
	club_name = models.CharField(max_length = 45)
	country = models.ForeignKey(Country)
	home_ground = models.ForeignKey(Venue)

	def __unicode__(self):
		return self.club_name

	@staticmethod
	def get_club(club_name):
		return Club.objects.get(club_name = club_name);

class TournamentBase(models.Model):
	TOURNAMENT_TYPE = (
		('CO', 'Country'),
		('CL', 'Club'),
	)
	tourn_cd = models.CharField(max_length = 5, primary_key=True)
	tourn_name = models.CharField(max_length = 30)
	tourn_desc = models.CharField(max_length = 50)
	country = models.ForeignKey(Country, null=True, blank=True)
	tournament_type = models.CharField(max_length=2, choices=TOURNAMENT_TYPE)

	@staticmethod
	def getTournamentBaseFromCode(tourn_cd):
		return TournamentBase.objects.filter(tourn_cd = tourn_cd)

	@staticmethod
	def getTournamentBaseFromName(tourn_name):
		return TournamentBase.objects.filter(tourn_name = tourn_name)

	@staticmethod
	def getTournamentBaseFromCountry(country):
		return TournamentBase.objects.filter(country = country)

class TournamentFormat(models.Model):
	tourn = models.ForeignKey(TournamentBase)
	no_of_teams = models.IntegerField(default = 0)
	no_of_gameweeks = models.IntegerField(default = 0)
	gw_cycle_day = models.CharField(max_length = 3)

	@staticmethod
	def getTournamentFormat(tournamentBase):
		return TournamentFormat.objects.filter(tourn = tournmentBase)

class Tournament(models.Model):
	tourn_format = models.ForeignKey(TournamentFormat)
	tourn_name = models.CharField(max_length = 45)
	season = models.CharField(max_length = 7)
	start_date = models.DateField(null = True, blank = True)
	end_date = models.DateField(null = True, blank = True)

	def __unicode__(self):
		return self.tourn_name

	def set_date_range(self):
		res = Match.objects.filter(tourn = self).aggregate(Min('match_date'), Max('match_date'))
		self.start_date = res.get('match_date__min')
		self.end_date = res.get('match_date__max')
		self.save()

	def normalize_gameweek(self):
		matches = Match.objects.filter(tourn = self).order_by('match_date')
		prev_gw = -1
		for match in matches:
			if prev_gw > match.gameweek_no:
				match.gameweek_no = prev_gw
				match.gameweek = Gameweek.get_gameweek(self, prev_gw)
				match.save()
			if prev_gw != match.gameweek_no:
				match.gameweek.lock_date = match.match_date
				match.gameweek.save()
			prev_gw = match.gameweek_no

	@staticmethod
	def getCurrentTournaments():
		return Tournament.objects.filter(start_date__lte = datetime.date.today()).filter(end_date__gte = datetime.date.today())

	@staticmethod
	def getTournamentFromTournamentCode(tournamentCode, currentSeason):
		return Tournament.objects.get(tourn_format__tourn__tourn_cd = tournamentCode, season = currentSeason)

class TournamentTeam(models.Model):
	tourn = models.ForeignKey(Tournament)
	team = models.ForeignKey(Team)

	@staticmethod
	def getTournamentTeam(tourn, team):
		return TournamentTeam.objects.get(tourn = tourn, team = team)

	@staticmethod
	def get_all_teams_by_tournament(tourn):
		return TournamentTeam.objects.filter(tourn = tourn)

class Gameweek(models.Model):
	tourn = models.ForeignKey(Tournament)
	gameweek_no = models.IntegerField()
	lock_date = models.DateTimeField()

	@staticmethod
	def get_gameweek(tourn, gameweek_no, add = False):
		obj = Gameweek.objects.filter(tourn = tourn, gameweek_no = gameweek_no)
		if obj.count() == 0:
			if add:
				Gameweek.objects.create(tourn = tourn, gameweek_no = gameweek_no, lock_date = datetime.datetime.now(pytz.UTC))
			else:
				return None
		return Gameweek.objects.get(tourn = tourn, gameweek_no = gameweek_no)

	@staticmethod
	def get_gameweek_obj(gameweek_no):
		return Gameweek.objects.get(gameweek_no = gameweek_no) #Wrong - There may be many tournaments with the same gameweek.

class Match(models.Model):
	match_api_id = models.IntegerField(primary_key = True)
	team1 = models.ForeignKey(Team, related_name = 'team1')
	team2 = models.ForeignKey(Team, related_name = 'team2')
	match_date = models.DateTimeField()
	tourn = models.ForeignKey(Tournament)
	venue = models.ForeignKey(Venue, null = True, blank = True)
	team1_score = models.IntegerField(null = True, blank = True)
	team2_score = models.IntegerField(null = True, blank = True)
	gameweek_no = models.IntegerField()
	gameweek = models.ForeignKey(Gameweek)

	@staticmethod
	def getFixtures(tournament, gameweek_number):
		return Match.objects.filter(tourn=tournament, gameweek_no=gameweek_number).order_by("match_date")

	@staticmethod
	def getMatchesOfDay(date):
		return Match.objects.filter(match_date=date)

	@staticmethod
	def getMatchesAfterDay(date):
		return Match.objects.filter(match_date__gt=date).order_by("match_date")

	@staticmethod
	def getTeams(match_id):
		return Match.objects.get(match_api_id =match_id)

	@staticmethod
	def getMatchId(match_id):
		return Match.objects.get(match_api_id =match_id)

	def __unicode__(self):
		return u'{0}'.format(self.match_api_id)

class Player(models.Model):
	PLAYER_TYPE = (
		('GK', 'Goalkeeper'),
		('DF', 'Defender'),
		('MF', 'Midfielder'),
		('ST', 'Striker'),
	)
	player_name = models.CharField(max_length = 45)
	current_club = models.ForeignKey(Club)
	nationality = models.ForeignKey(Country)
	player_type = models.CharField(max_length = 2, choices = PLAYER_TYPE)
	player_api_id = models.IntegerField(null = True, blank = True)

	@staticmethod
	def get_player_from_playername_and_team(player_name, team):
		return Player.objects.filter(player_name=player_name, current_club=team.club)

	@staticmethod
	def validate(player_id, player_type = None):
		p = Player.objects.filter(id = player_id)
		return p.count() > 0 and (player_type == None or p[0].player_type == player_type)

	@staticmethod
	def validate_two_players(player1, player2):
		p1 = Player.objects.filter(id = player1)
		p2 = Player.objects.filter(id = player2)
		return p1.count() > 0 and p2.count() > 0 and p1[0].player_type == p2[0].player_type

	@staticmethod
	def get_player_from_playerId(playerId):
		return Player.objects.get(player_api_id = playerId)
	
	def __unicode__(self):
		return self.player_name

class Squad(models.Model):
	tourn_team = models.ForeignKey(TournamentTeam)
	player = models.ForeignKey(Player)
	is_active = models.BooleanField(default = False)
	current_cost = models.DecimalField(max_digits = 3, decimal_places=1)

	@staticmethod
	def update_price(player_id, price):
		player = Player.objects.get(id = player_id)
		squad_member = Squad.objects.get(player = player)
		squad_member.current_cost = price
		squad_member.save()
		return True

	@staticmethod
	def get_player_for_team(tourn, team, player_type):
		if team == 'ALL':
			tourn_team = TournamentTeam.get_all_teams_by_tournament(tourn)
		else:
			tourn_team = TournamentTeam.getTournamentTeam(tourn, team)
		if player_type == 'ALL':
			return Squad.objects.filter(tourn_team = tourn_team, is_active = True)
		else:
			return Squad.objects.filter(tourn_team = tourn_team, is_active = True, player__player_type = player_type)

	@staticmethod
	def get_player_value(player):
		return Squad.objects.filter(player = player)[0]

	@staticmethod
	def get_cost_for_player(tourn, player_id):
		player = Squad.objects.filter(player = player_id, tourn_team__tourn = tourn)
		if player.count() > 0:
			return player[0].current_cost
		return -1

class MatchPlayerDetails(models.Model):
	match = models.ForeignKey(Match)
	player = models.ForeignKey(Player)
	team = models.ForeignKey(Team)
	started = models.BooleanField(default = False)
	mins_played = models.IntegerField(default = 0)
	goals_scored = models.IntegerField(default = 0)
	assists = models.IntegerField(default = 0)
	saves = models.IntegerField(default = 0)
	yellow_card = models.BooleanField(default = False)
	red_card = models.BooleanField(default = False)
	own_goal = models.IntegerField(default = 0)
	points = models.IntegerField(default = 0)

	@staticmethod
	def get_total_pts_by_player_and_tourn(player, tourn):
		matches = Match.objects.filter(tourn = tourn)
		pts = MatchPlayerDetails.objects.filter(match__in = matches, player = player).aggregate(Sum('points')).get('points__sum')
		return 0 if pts == None else pts

	@staticmethod
	def get_total_pts_by_player_and_tourn_gameweek(player, tourn, gameweek):
		matches = Match.objects.filter(tourn = tourn, gameweek = Gameweek.get_gameweek(tourn, gameweek))
		pts = MatchPlayerDetails.objects.filter(match__in = matches, player = player).aggregate(Sum('points')).get('points__sum')
		return 0 if pts == None else pts

	@staticmethod
	def get_players_from_team(match_id,team_id):
		return MatchPlayerDetails.objects.filter(match = match_id,team = team_id)

	@staticmethod
	def get_hot_players(tournament, last_gameweek):
		return MatchPlayerDetails.objects.filter(match__in = (Match.objects.filter(gameweek = last_gameweek, tourn = tournament))).order_by("-points")[:15]

class UserProfile(models.Model):
	user = models.OneToOneField(User, primary_key=True)
	fav_club = models.ForeignKey(Club, null = True, blank = True)
	fav_country = models.ForeignKey(Country, null = True, blank = True)
	fav_player = models.ForeignKey(Player, null = True, blank = True)

	@staticmethod
	def getUserProfile(user):
		return UserProfile.objects.filter(user = user)

class Game(models.Model):
	GAME_TYPE = (
		('F', 'Footopia'),
		('P', 'Prediction'),
	)
	tourn = models.ForeignKey(Tournament)
	game_type = models.CharField(max_length = 1, choices = GAME_TYPE)
	#Used only for footopia
	allowed_transfers = models.IntegerField(blank = True, null = True)
	allowed_wildcards = models.IntegerField(blank = True, null = True)

	@staticmethod
	def getGame(tournament, game_type):
		return Game.objects.filter(tourn = tournament, game_type = game_type)[0]

class UserEnrollment(models.Model):
	game = models.ForeignKey(Game)
	user = models.ForeignKey(User)
	fav_team = models.ForeignKey(Team)
	total_pts = models.IntegerField()

	@staticmethod
	@transaction.atomic
	def enroll_user(user, tournament_code, season, fav_team, g_type = 'P'):
		game = Game.objects.get(tourn = Tournament.getTournamentFromTournamentCode(tournament_code, season), game_type = g_type)
		enroll = UserEnrollment(game = game, user = user, fav_team = Team.objects.get(id=fav_team), total_pts = 0)
		enroll.save()
		if g_type == 'F':
			UserEnrollmentFootopia.objects.create(user_enroll = enroll, transfers_remaining = game.allowed_transfers, wildcards_remaining = game.allowed_wildcards)
		GameLeague.add_or_create_League_user(user, game, fav_team)

	@staticmethod
	def is_enrolled(user, tournament, g_type):
		game = Game.objects.get(tourn = tournament, game_type = g_type)
		return UserEnrollment.objects.filter(user = user, game = game).count() > 0

	@staticmethod
	def getUserEnrollmentPoints(user, game):
		return UserEnrollment.objects.filter(user = user, game = game)

	@staticmethod
	def getPoints(user, tournamentCode, season, g_type = 'P'):
		game = Game.objects.get(tourn = Tournament.getTournamentFromTournamentCode(tournamentCode, season), game_type = g_type)
		return UserEnrollment.objects.get(user = user, game = game).total_pts

	@staticmethod
	def getAllEnrollments(user):
		return UserEnrollment.objects.filter(user = user)

	@staticmethod
	def getTopUsers(tournamentCode, season, g_type = 'P'):
		game = Game.objects.get(tourn = Tournament.getTournamentFromTournamentCode(tournamentCode, season), game_type = g_type)
		return UserEnrollment.objects.filter(game = game).order_by("-total_pts")[:10]

	@staticmethod
	def getRank(user, tournamentCode, season, g_type = 'P'):
		game = Game.objects.get(tourn = Tournament.getTournamentFromTournamentCode(tournamentCode, season), game_type = g_type)
		myPoint = UserEnrollment.getPoints(user, tournamentCode, season, g_type)
		aboveMe = len(UserEnrollment.objects.filter(game = game, total_pts__gt=myPoint)) + 1
		return str(aboveMe) +"/"+ str(UserEnrollment.objects.filter(game = game).count())

	@staticmethod
	def getPredictionEnrollments(user, tournament):
		game = Game.objects.get(tourn = tournament, game_type = 'P')
		return UserEnrollment.objects.filter(game = game, user = user)
	
	@staticmethod
	def get_footopia_enrollments(tourn):
		return UserEnrollment.objects.filter(game = Game.objects.get(tourn = tourn, game_type = 'F'))

	@staticmethod
	def get_footopia_enrollment_for_user(user, tournament):
		return  UserEnrollment.objects.filter(user = user, game = Game.objects.get(tourn = tournament, game_type = 'F'))

		
class UserEnrollmentFootopia(models.Model):
	user_enroll = models.OneToOneField(UserEnrollment)
	transfers_remaining = models.IntegerField()
	wildcards_remaining = models.IntegerField()

	@staticmethod
	def is_transfers_remaining(tourn, user, transfers):
		game = Game.objects.get(tourn = tourn, game_type = 'F')
		enroll = UserEnrollment.objects.get(user = user, game = game).userenrollmentfootopia
		return enroll.transfers_remaining >= transfers

	@staticmethod
	def is_wildcard_remaining(tourn, user):
		game = Game.objects.get(tourn = tourn, game_type = 'F')
		enroll = UserEnrollment.objects.get(user = user, game = game).userenrollmentfootopia
		return enroll.wildcards_remaining > 0

	@staticmethod
	def get_transfers_and_wildcards(tourn, user):
		game = Game.objects.get(tourn = tourn, game_type = 'F')
		enroll = UserEnrollment.objects.get(user = user, game = game).userenrollmentfootopia
		return (enroll.transfers_remaining, enroll.wildcards_remaining)

	@staticmethod
	def update_transfers(tourn, user, tr_cnt, is_wildcard):
		game = Game.objects.get(tourn = tourn, game_type = 'F')
		enroll = UserEnrollment.objects.get(user = user, game = game).userenrollmentfootopia
		if is_wildcard:
			enroll.wildcards_remaining = enroll.wildcards_remaining - 1
		else:
			enroll.transfers_remaining = enroll.transfers_remaining - tr_cnt
		enroll.save()

class UserPrediction(models.Model):
	match = models.ForeignKey(Match)
	user = models.ForeignKey(User)
	team1_score = models.IntegerField()
	team2_score = models.IntegerField()
	points = models.IntegerField(default = 0)

	@staticmethod
	def add_or_update_prediction(user, match, team1_score, team2_score):
		qs = UserPrediction.objects.filter(user = user, match = match)
		if qs.count() > 0:
			user_pred = qs[0]
		else:
			user_pred = UserPrediction()
			user_pred.match = match
			user_pred.user = user
		user_pred.team1_score = team1_score
		user_pred.team2_score = team2_score
		user_pred.save()

class PointSystem(models.Model):
	RULES = (
		('P_EXA', 'Correct result and score'),
		('P_RGD', 'Correct result and goal difference'),
		('P_RES', 'Correct result'),
		('P_ICR', 'Incorrect result'),
		('F_GKS', 'Goalkeeper scores goal'),
		('F_DFS', 'Defender scores goal'),
		('F_MFS', 'Midfielder scores goal'),
		('F_STS', 'Striker scores goal'),
		('F_OWN', 'Player scores own goal'),
		('F_YEL', 'Player gets yellow card'),
		('F_RED', 'Player gets red card'),
		('F_MPD', 'Player played minutes')
	)
	rule = models.CharField(max_length = 5, choices = RULES, primary_key = True)
	points = models.IntegerField()

	@staticmethod
	def get_points(rule):
		return (PointSystem.objects.get(rule=rule)).points

class TeamStandings(models.Model):
	tourn = models.ForeignKey(Tournament)
	team = models.ForeignKey(Team)
	position = models.IntegerField()
	played = models.IntegerField()
	points = models.IntegerField()

	@staticmethod
	def getAll(tourn):
		return TeamStandings.objects.filter(tourn = tourn).order_by("position")

class TeamSelection(models.Model):
	gameweek = models.ForeignKey(Gameweek)
	user = models.ForeignKey(User)
	player = models.ForeignKey(Player)
	price = models.IntegerField()

	@staticmethod
	def team_exists(tourn, user):
		return TeamSelection.objects.filter(user = user, gameweek = Gameweek.objects.filter(tourn = tourn)).count() > 0

	@staticmethod
	def getTeamDetails(game_week,user):
		return TeamSelection.objects.filter(user = user, gameweek = game_week)

	@staticmethod
	def get_first_gw_selection(tourn, user):
		res = TeamSelection.objects.filter(user = user, gameweek = Gameweek.objects.filter(tourn = tourn)).aggregate(Min('gameweek__gameweek_no'))
		return res['gameweek__gameweek_no__min']

	@staticmethod
	def add_team(tourn, start_gw, end_gw, user, player_list):
		team_list = []
		for gw in range(start_gw, end_gw + 1):
			gw_obj = Gameweek.get_gameweek(tourn, gw, add = True)
			for player in player_list:
				obj = TeamSelection()
				obj.gameweek = gw_obj
				obj.user = user
				obj.player = player
				obj.price = Squad.get_cost_for_player(tourn, player)
				team_list.append(obj)
		TeamSelection.objects.bulk_create(team_list)

	@staticmethod
	def is_player_in_team(tourn, gw, user, player_id):
		gw = Gameweek.get_gameweek(tourn, gw)
		if gw == None: return False
		return TeamSelection.objects.filter(gameweek = gw, user = user, player = player_id).count > 0

	@staticmethod
	def update_team(tourn, start_gw, user, edit_player_list, is_wildcard):
		#Get all objects in team selection of user from start_gw
		selection = TeamSelection.objects.filter(user = user, gameweek__tourn = tourn, gameweek__gameweek_no__gte = start_gw)
		for swap in edit_player_list:
			selection.filter(player=swap[0]).update(player=swap[1])
		UserEnrollmentFootopia.update_transfers(tourn, user, len(edit_player_list), is_wildcard)


class FootopiaPoints(models.Model):
	user_enrollment = models.ForeignKey(UserEnrollment)
	gameweek = models.ForeignKey(Gameweek)
	points = models.IntegerField()

	@staticmethod
	def get_user_gameweek_points(tourn, gameweek, user):
		user_enrollment = UserEnrollment.objects.get(user = user, game_id = (Game.objects.get(tourn = tourn, game_type = "F")))
		return FootopiaPoints.objects.filter(user_enrollment = user_enrollment, gameweek = Gameweek.get_gameweek(tourn, gameweek))

	@staticmethod
	def get_highest_point(tourn, gameweek):
		footopiaObj = FootopiaPoints.objects.filter(gameweek = Gameweek.get_gameweek(tourn, gameweek)).order_by("-points")
		highPt = 0
		if not footopiaObj.count() == 0:
			highPt = footopiaObj[0].points
		return highPt

	@staticmethod
	def get_average_point(tourn, gameweek):
		footopiaObj = FootopiaPoints.objects.filter(gameweek = Gameweek.get_gameweek(tourn, gameweek))
		avgPt = 0
		if not footopiaObj.count() == 0:
			avgPt = footopiaObj.aggregate(Avg('points')).get('points__avg')
		return avgPt

	@staticmethod
	def add_or_update_points(user_enr, gameweek, footopia_points):
		try:
			obj = FootopiaPoints.objects.get(user_enrollment = user_enr, gameweek = gameweek)
			obj.points = footopia_points
			obj.save()
		except:
			FootopiaPoints.objects.create(user_enrollment = user_enr, gameweek = gameweek, points = footopia_points)

	@staticmethod
	def get_points(user_enrollment, gameweek):
		obj = FootopiaPoints.objects.filter(user_enrollment = user_enrollment, gameweek = gameweek)
		if obj.count() == 0:
			return 0
		return FootopiaPoints.objects.filter(user_enrollment = user_enrollment, gameweek = gameweek).points

class PredictionPoints(models.Model):
	user_enrollment = models.ForeignKey(UserEnrollment)
	gameweek = models.ForeignKey(Gameweek)
	points = models.IntegerField()

	@staticmethod
	def get_points(user_enrollment, gameweek):
		obj = PredictionPoints.objects.filter(user_enrollment = user_enrollment, gameweek = gameweek)
		if obj.count() == 0:
			return 0
		return PredictionPoints.objects.filter(user_enrollment = user_enrollment, gameweek = gameweek).points

class GameLeague(models.Model):
	game = models.ForeignKey(Game)
	user = models.ForeignKey(User, null=True)
	users = models.ManyToManyField(User, related_name='league_users')
	name = models.CharField(max_length = 30)
	description = models.CharField(max_length = 200)
	uniqueCode = models.CharField(max_length = 60)
	is_private = models.BooleanField(default = True)
	gameweek = models.ForeignKey(Gameweek)

	@staticmethod
	def getUserGameLeague(user, tournamentCode, season, g_type):
		game = Game.objects.get(tourn = Tournament.getTournamentFromTournamentCode(tournamentCode, season), game_type = g_type)
		return GameLeague.objects.filter(Q(user = user)| Q(users__id = user.id), game = game)

	@staticmethod
	def createLeague(user, tournamentCode, season, g_type, name, description, gameweek, is_private = True):
		tourn = Tournament.getTournamentFromTournamentCode(tournamentCode, season)
		game = Game.objects.get(tourn = tourn, game_type = g_type)
		league = GameLeague(game = game, user = user, name = name, description = description, uniqueCode = g_type+str(user.id)+str(game.id)+name.replace(' ', '')+season, gameweek = gameweek, is_private = is_private)
		league.save()
		return league.uniqueCode

	@staticmethod
	def add_or_create_League_user(user, game, fav_team):
		team = Team.objects.get(id = fav_team)
		obj = GameLeague.objects.filter(game = game, name = team.club.club_name+' League', is_private = False)
		if obj.count() >0:
			obj[0].users.add(user)
			obj[0].save()
		else:
			gameweek = Gameweek.get_gameweek(game.tourn, 1)
			league = GameLeague(game = game, name = team.club.club_name+' League', description = 'This league is for '+team.club.club_name+' Team fans to compete and interact with each other !', uniqueCode = team.club.club_name+str(game.id), gameweek = gameweek, is_private = False)
			league.save()
			league.users.add(user)
			league.save()


	@staticmethod
	def addUser(user, uCode):
		gameLeague = GameLeague.objects.get(uniqueCode = uCode)
		gameLeague.users.add(user)
		gameLeague.save()
		return True

	@staticmethod
	def isValidCode(uCode, tournamentCode, season, g_type):
		tourn = Tournament.getTournamentFromTournamentCode(tournamentCode, season)
		game = Game.objects.get(tourn = tourn, game_type = g_type)
		obj = GameLeague.objects.filter(uniqueCode = uCode, game= game, is_private = True)
		if obj.count() == 0:
			return False
		return True

	@staticmethod
	def isUserExist(user, uCode):
		obj = GameLeague.objects.filter(Q(user = user)| Q(users__id = user.id), uniqueCode = uCode)
		if obj.count() == 0:
			return False
		return True

	@staticmethod
	def getPredictionScore(league_id, currentGameWeek, tournamentCode, season):
		tournament = Tournament.getTournamentFromTournamentCode(tournamentCode, season)
		game = Game.objects.get(tourn = tournament, game_type = 'P')
		leaderDict = {}
		gameLeague = GameLeague.objects.get(id = league_id)
		start = gameLeague.gameweek.gameweek_no
		user_enrollement = UserEnrollment.objects.filter(user = gameLeague.user, game = game)
		total_pts = 0
		if user_enrollement.count() >0:
			for i in range (start, currentGameWeek+1):
				gameWeek = Gameweek.objects.get(tourn = tournament, gameweek_no = i)
				total_pts  = total_pts + PredictionPoints.get_points(user_enrollment = user_enrollement[0], gameweek= gameWeek)
			leaderDict[gameLeague.user] = total_pts
		for user in gameLeague.users.all():
			user_enrollement = UserEnrollment.objects.get(user = user, game = game)
			for i in range (start, currentGameWeek):
				gameWeek = Gameweek.objects.get(tourn = tournament, gameweek_no = i)
				total_pts  = total_pts + PredictionPoints.get_points(user_enrollment = user_enrollement, gameweek= gameWeek)
			leaderDict[user] = total_pts
		result = sorted(leaderDict.items(), key=lambda x: x[1], reverse=True)
		return result

	@staticmethod
	def getFootopiaScore(league_id, currentGameWeek, tournamentCode, season):
		tournament = Tournament.getTournamentFromTournamentCode(tournamentCode, season)
		game = Game.objects.get(tourn = tournament, game_type = 'F')
		leaderDict = {}
		gameLeague = GameLeague.objects.get(id = league_id)
		start = gameLeague.gameweek.gameweek_no
		user_enrollement = UserEnrollment.objects.filter(user = gameLeague.user, game = game)
		total_pts = 0
		if user_enrollement.count() >0:
			for i in range (start, currentGameWeek+1):
				gameWeek = Gameweek.objects.get(tourn = tournament, gameweek_no = i)
				total_pts  = total_pts + FootopiaPoints.get_points(user_enrollment = user_enrollement[0], gameweek= gameWeek)
			leaderDict[gameLeague.user] = total_pts
		for user in gameLeague.users.all():
			user_enrollement = UserEnrollment.objects.get(user = user, game = game)
			for i in range (start, currentGameWeek):
				gameWeek = Gameweek.objects.get(tourn = tournament, gameweek_no = i)
				total_pts  = total_pts + FootopiaPoints.get_points(user_enrollment = user_enrollement, gameweek= gameWeek)
			leaderDict[user] = total_pts
		result = sorted(leaderDict.items(), key=lambda x: x[1], reverse=True)
		return result

class PlayerStatistics(models.Model):
	squad = models.OneToOneField(Squad)
	total_mins_played = models.IntegerField(default=0)
	total_goals = models.IntegerField(default=0)
	total_yellow_cards = models.IntegerField(default=0)
	total_red_cards = models.IntegerField(default=0)
	total_own_goals = models.IntegerField(default=0)
	avg_rate_of_scoring = models.DecimalField(max_digits = 3, decimal_places=1)
	player_rating = models.DecimalField(max_digits = 3, decimal_places=1)

	@staticmethod
	def add_detail_or_update(current_detail):
		stat = PlayerStatistics.objects.filter(squad = current_detail.squad_player)
		if len(stat) == 0:
			stat = PlayerStatistics()
		else:
			stat = stat[0]
		stat.squad = current_detail.squad_player
		stat.total_mins_played = current_detail.minutes_played
		stat.total_goals = current_detail.goals_scored
		stat.total_yellow_cards = current_detail.yellow_cards
		stat.total_red_cards = current_detail.red_cards
		stat.total_own_goals = current_detail.own_goals
		stat.avg_rate_of_scoring = current_detail.avg_rate_of_scoring
		stat.player_rating = current_detail.player_rating
		stat.save()

	@staticmethod
	def get_top_scorers_utils(tournament):
		return PlayerStatistics.objects.filter(squad__in=(Squad.objects.filter(tourn_team__in=(TournamentTeam.objects.filter(tourn = tournament))))).order_by("-total_goals")[:10]

	@staticmethod
	def get_all_player_utils(tournament):
		return PlayerStatistics.objects.filter(squad__in=(Squad.objects.filter(tourn_team__in=(TournamentTeam.objects.filter(tourn = tournament))).order_by("tourn_team")))
