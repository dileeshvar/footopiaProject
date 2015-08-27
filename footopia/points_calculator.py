from footopia.models import *
from model_utils import *

def load_points_rules():
	rules = {'P_EXA':30, 'P_RGD':20, 'P_RES':10, 'P_ICR':-10, 'F_GKS':5, 'F_DFS':4, 'F_MFS':3, 'F_STS':3, 'F_OWN':-3, 'F_YEL':-1, 'F_RED':-5, 'F_MPD':1}
	for rule in rules:
		PointSystem.objects.create(rule=rule, points = rules[rule])

def calculate_footopia_points_for_tournament(tournament):
	current_gameweek = getGameWeek(tournament)
	gameweeks = Gameweek.objects.filter(tourn = tournament, gameweek_no__lte = current_gameweek)
	for gameweek in gameweeks:
		calculate_footopia_points_for_gameweek(gameweek)
	calculate_footopia_total_score(tournament)

def calculate_footopia_points_for_gameweek(gameweek):
	user_enrollments = UserEnrollment.get_footopia_enrollments(gameweek.tourn)
	for user_enr in user_enrollments:
		user = user_enr.user
		currentTeam = TeamSelection.objects.filter(gameweek = gameweek, user = user).values("player")
		footopia_points = MatchPlayerDetails.objects.filter(match__in = Match.objects.filter(gameweek = gameweek), player__in = (currentTeam)).aggregate(Sum("points")).get("points__sum")
		if footopia_points == None: footopia_points = 0
		# for player_detail in details:
			# for player in currentTeam:
				# if player_detail.player == player.player:
					# player_seen_count = player_seen_count + 1
					# footopia_points = footopia_points + player_detail.points
					# break
				# if player_seen_count == 11:
					# break
		FootopiaPoints.add_or_update_points(user_enr, gameweek, footopia_points)
	
def calculate_footopia_total_score(tourn):
	user_enrollments = UserEnrollment.get_footopia_enrollments(tourn)
	for enrollment in user_enrollments:
		current_footopia = FootopiaPoints.objects.filter(gameweek__tourn = tourn, user_enrollment = enrollment)
		enrollment.total_pts = current_footopia.aggregate(Sum("points")).get("points__sum")
		enrollment.save()

def get_player_points(player_details):
	points = 0
	if player_details.mins_played > 45:
		factor = int(player_details.mins_played / 45)
		points = points + (factor * PointSystem.get_points('F_MPD'))
	if player_details.goals_scored > 0:
		if player_details.player.player_type == 'GK':	
			points = points + int(player_details.goals_scored)*(PointSystem.get_points('F_GKS'))
		if player_details.player.player_type == 'DF':	
			points = points + int(player_details.goals_scored)*(PointSystem.get_points('F_DFS'))
		if player_details.player.player_type == 'MF':	
			points = points + int(player_details.goals_scored)*(PointSystem.get_points('F_MFS'))
		if player_details.player.player_type == 'ST':	
			points = points + int(player_details.goals_scored)*(PointSystem.get_points('F_STS'))
	if player_details.own_goal > 0:
		points = points + int(player_details.own_goal)*(PointSystem.get_points('F_OWN'))
	if player_details.yellow_card == True:
		points = points + PointSystem.get_points('F_YEL')
	if player_details.red_card == True:
		points = points + PointSystem.get_points('F_RED')
	return points
	
def update_prediction_points_for_match(tournament, updating_match):
	prediction_scoring = UserPrediction.objects.filter(match=updating_match)
	for prediction in prediction_scoring:
		prediction.points = get_points_for_prediction(updating_match, prediction)
		update_overall_points_for_prediction(tournament, prediction)
		update_gameweek_points_for_prediction(tournament, prediction.points, updating_match.gameweek, prediction.user)
		prediction.save()
	
def get_points_for_prediction(match, prediction):
	status = ""
	if match.team1_score == prediction.team1_score and match.team2_score == prediction.team2_score:
		status = "P_EXA"
	elif match.team1_score - match.team2_score == prediction.team1_score - prediction.team2_score:
		status = "P_RGD"
	elif match.team2_score - match.team1_score > 0 and prediction.team2_score - prediction.team1_score > 0:
		status = "P_RES"
	elif match.team2_score - match.team1_score < 0 and prediction.team2_score - prediction.team1_score < 0:
		status = "P_RES"
	else:
		status = "P_ICR"
	return PointSystem.objects.get(rule=status).points
	
def update_overall_points_for_prediction(tournament, prediction):
	game = Game.objects.get(tourn = tournament, game_type="P")
	userEnrollment = UserEnrollment.objects.get(game=game, user=prediction.user)
	userEnrollment.total_pts = userEnrollment.total_pts + prediction.points
	userEnrollment.save()

def update_gameweek_points_for_prediction(tournament, points, gameweek, user):
	user_enrollment = UserEnrollment.getPredictionEnrollments(user, tournament)
	gameweek_prediction = PredictionPoints.objects.filter(user_enrollment = user_enrollment, gameweek = gameweek)
	if len(gameweek_prediction) == 0:
		gameweek_update = PredictionPoints.objects.create(user_enrollment = user_enrollment, gameweek = gameweek, points = 0)
	else:
		gameweek_update = gameweek_prediction[0]
	gameweek_update.points = gameweek_update.points + points
	gameweek_update.save()