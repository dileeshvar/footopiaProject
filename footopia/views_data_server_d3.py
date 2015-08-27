from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from decorators import *
from footopia.model_utils import *
from footopia.models import *
import csv
import shutil
import os

@login_required
@tourn_code_season_validator
def serve_d3_chart_for_prediction(request, tournamentCode, season):
	tourn_cd = tournamentCode
	season = season
	tournament = Tournament.getTournamentFromTournamentCode(tourn_cd, season)
	points = populate_data_for_chart_in_prediction(request.user, tournament)
	cwd = os.getcwd()
	csv_path = 'footopia/templates/data/data_user_prediction_points.csv'
	csv_path = os.path.join(cwd, csv_path)
	with open(csv_path, 'w') as csvfile:		
		fieldnames = ['gameweek', 'points']
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',', lineterminator='\n')
		writer.writeheader()
		for point in points:
			writer.writerow({'gameweek': 'gameweek '+ str(point[0]), 'points': point[1]})
	return render(request, "data/data_user_prediction_points.csv", content_type='text/csv')	

def populate_data_for_chart_in_prediction(user, tournament):
	user_enrollment = UserEnrollment.getPredictionEnrollments(user, tournament)
	past_predictions = PredictionPoints.objects.filter(user_enrollment=user_enrollment).order_by("-gameweek")
	points_gameweeks = []
	if len(past_predictions) != 0:
		last_gameweek = past_predictions[0].gameweek
		for i in range(len(past_predictions)):
			tuple = (past_predictions[i].gameweek.gameweek_no, past_predictions[i].points)
			points_gameweeks.append(tuple)
	return points_gameweeks

@login_required
@tourn_code_season_validator
def serve_d3_chart_for_footopia(request, tournamentCode, season):
	tourn_cd = tournamentCode
	season = season
	tournament = Tournament.getTournamentFromTournamentCode(tourn_cd, season)
	points = populate_data_for_chart_in_footopia(request.user, tournament)
	cwd = os.getcwd()
	csv_path = 'footopia/templates/data/data_user_footopia_points.csv'
	csv_path = os.path.join(cwd, csv_path)
	with open(csv_path, 'w') as csvfile:
		fieldnames = ['gameweek', 'points']
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',', lineterminator='\n')
		writer.writeheader()
		for point in points:
			writer.writerow({'gameweek': 'gameweek '+ str(point[0]), 'points': point[1]})
	return render(request, "data/data_user_footopia_points.csv", content_type='text/csv')	
	
def populate_data_for_chart_in_footopia(user, tourn):
	user_enr = UserEnrollment.get_footopia_enrollment_for_user(user, tourn)
	past_footopias = FootopiaPoints.objects.filter(user_enrollment = user_enr).order_by("-gameweek")
	points_gameweeks = []
	if len(past_footopias) != 0:
		last_gameweek = past_footopias[0].gameweek
		for i in range(len(past_footopias)):
			tuple = (past_footopias[i].gameweek.gameweek_no, past_footopias[i].points)
			points_gameweeks.append(tuple)
	return points_gameweeks