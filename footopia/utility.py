import datetime
	
def convert_season_string(season):
	if len(season) == 7:
		return season[2:4] + season[5:]
	else:
		return season
		
def get_team_code_from_name(team_name):
	return team_name[:3].upper()
	
def get_player_last_name(player_name):
	player_name = player_name.strip()
	if " " in player_name:
		return player_name[0] +" "+ player_name[(player_name.index(" ") + 1):]
	return player_name