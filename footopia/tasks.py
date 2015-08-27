from footopiaproj import celery_app
import bg_utils
from footopia.models import *

@celery_app.task
def load_tournament_data(tid):
	bg_utils.load_tournament_data(Tournament.objects.get(id=tid))
	
@celery_app.task
def refresh_tournaments():
	for tourn in Tournament.getCurrentTournaments():
		bg_utils.refresh_tournament(tourn)

@celery_app.task		
def update_results():
	for tourn in Tournament.getCurrentTournaments():
		bg_utils.refresh_results(tourn)