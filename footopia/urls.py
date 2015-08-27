from django.conf.urls import patterns, include, url
from footopia.forms_register import *
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin

urlpatterns = patterns('',
    url(r'^$', 'footopia.views.home',name='home'),
    url(r'^home$', 'footopia.views.home',name='home'),

	# Login and registration urls
    url(r'^login$', 'django.contrib.auth.views.login', {'template_name':'home.html',
    'extra_context':{'R_form':RegistrationForm,'Reset_form':ResetForm}}, name='login'),
	url(r'^logout$', 'django.contrib.auth.views.logout_then_login', name='logout'),
	url(r'^register$', "footopia.views_login_register.register", name='register'),
	url(r'^reset$', "footopia.views_login_register.reset", name='reset'),
	url(r'^reset-password/(?P<username>[a-zA-Z0-9_@\+\-]+)/resetPass$', 'footopia.views_login_register.resetDone', name='resetPass'),

	# The following URL should match any username valid in Django and
    # any token produced by the default_token_generator
    url(r'^confirm-registration/(?P<username>[a-zA-Z0-9_@\+\-]+)/(?P<token>[a-z0-9\-]+)$', 'footopia.views_login_register.confirm_registration', name='confirm'),
	url(r'^reset-password/(?P<username>[a-zA-Z0-9_@\+\-]+)/(?P<token>[a-z0-9\-]+)$', 'footopia.views_login_register.reset_password', name='reset'),

	# Redirection for home of main pages
	# url(r'^(?P<userId>\d+)/dashboard$', 'footopia.views.dashboard', name='dashboard'),
	url(r'^(?P<tournamentCode>\w+)/(?P<season>[0-9\-]+)/view-tournament$', 'footopia.views.view_tournament', name='view_tournament'),
	url(r'^(?P<tournamentCode>\w+)/(?P<season>[0-9\-]+)/view-tournament/get-fixtures$', 'footopia.views.get_fixtures_home', name='get_fixtures_home'),
	url(r'^(?P<tournamentCode>\w+)/(?P<season>[0-9\-]+)/view-tournament/get-matchinfo$', 'footopia.views.displayMatch',name='displayMatch'),
	# General list of actions which can be performed from anywhere in the application
	# url(r'^squad/view-real-team/(?P<teamName>\w+)$', 'footopia.views.view_team', name='view_team'),
	# url(r'^squad/view-player/(?P<playerId>\d+)$', 'footopia.views.view_player', name='view_player'),

	# User related actions
	url(r'^(?P<userId>\d+)/view-profile$', 'footopia.views_user_profile.show_profile', name='view_user_profile'),
	url(r'^get-upcoming-games$', 'footopia.views.get_upcoming_games', name='get_upcoming_games'),
	# url(r'^(?P<userId>\d+)/edit-profile$', 'footopia.views.edit_my_profile', name='edit_my_profile'),
	# url(r'^(?P<userId>\d+)/save-profile$', 'footopia.views.save_my_profile', name='save_my_profile'),
	# url(r'^(?P<userId>\d+)/view-footopia-profile$', 'footopia.views.view_footopia_profile', name='view_footopia_profile'),
	# url(r'^(?P<userId>\d+)/view-prediction-profile$', 'footopia.views.view_prediction_profile', name='view_prediction_profile'),

	# actions performed from Prediction page urls
	url(r'^(?P<tournamentCode>\w+)/(?P<season>[0-9\-]+)/prediction/join-tournament$', 'footopia.views_prediction.join_tournament', name='join_prediction'),
	url(r'^(?P<tournamentCode>\w+)/(?P<season>[0-9\-]+)/prediction/home$', 'footopia.views_prediction.home', name='predict_home'),
	url(r'^(?P<tournamentCode>\w+)/(?P<season>[0-9\-]+)/prediction/get-fixtures$', 'footopia.views_prediction.get_fixtures', name='get_fixtures'),
	# url(r'^(?P<tournamentCode>\w+)/(?P<season>[0-9\-]+)/prediction/view-team-form$', 'footopia.views_prediction.view_team_form', name='view_team_form'),
	url(r'^(?P<tournamentCode>\w+)/(?P<season>[0-9\-]+)/prediction/predict$', 'footopia.views_prediction.predict', name='predict'),
	url(r'^(?P<tournamentCode>\w+)/(?P<season>[0-9\-]+)/prediction/show-my-leagues$', 'footopia.views_prediction.get_my_leagues', name='p_get_my_leagues'),
	# url(r'^(?P<tournamentCode>\w+)/(?P<season>[0-9\-]+)/prediction/search-for-leagues/(?P<searchName>\w+)$', 'footopia.views_prediction.search_for_leagues', name='search_for_leagues')
	url(r'^(?P<tournamentCode>\w+)/(?P<season>[0-9\-]+)/prediction/create-my-league$', 'footopia.views_prediction.create_new_league', name='p_create_new_league'),
    url(r'^(?P<tournamentCode>\w+)/(?P<season>[0-9\-]+)/prediction/join-league$', 'footopia.views_prediction.join_league', name='p_join_league'),
	# url(r'^(?P<tournamentCode>\w+/(?P<season>[0-9\-]+))/prediction/view-league-statistics/(?P<leagueId>\d+)$', 'footopia.views_prediction.view_league_statistics', name='view_league_statistics')
	url(r'^(?P<tournamentCode>\w+)/(?P<season>[0-9\-]+)/prediction/view-league/(?P<leagueId>\d+)$', 'footopia.views_prediction.view_league', name='p_view_league'),
	# url(r'^(?P<tournamentCode>\w+)/(?P<season>[0-9\-]+)/prediction/view-past-prediction-records/(?P<userId>\d+)$', 'footopia.views_prediction.view_past_prediction_records', name='view_past_prediction_records'),
	url(r'^(?P<tournamentCode>\w+)/(?P<season>[0-9\-]+)/prediction/p_rules$', 'footopia.views_prediction.rules', name='p_rules'),

	# actions performed from footopia page urls
	url(r'^(?P<tournamentCode>\w+)/(?P<season>[0-9\-]+)/footopia/join-tournament$', 'footopia.views_footopia.join_tournament', name='join_footopia'),
	url(r'^(?P<tournamentCode>\w+)/(?P<season>[0-9\-]+)/footopia/home$', 'footopia.views_footopia.home', name='footopia_home'),
	url(r'^(?P<tournamentCode>\w+)/(?P<season>[0-9\-]+)/footopia/create-my-team$', 'footopia.views_footopia.create_team', name='create_team'),
	url(r'^(?P<tournamentCode>\w+)/(?P<season>[0-9\-]+)/footopia/edit-my-team$', 'footopia.views_footopia.edit_team', name='edit_team'),
	url(r'^(?P<tournamentCode>\w+)/(?P<season>[0-9\-]+)/footopia/get-players$', 'footopia.views_footopia.get_players', name='get_players'),
	url(r'^(?P<tournamentCode>\w+)/(?P<season>[0-9\-]+)/footopia/get-teamdetails$', 'footopia.views_footopia.get_teamdetails', name='get_teamdetails'),
    url(r'^(?P<tournamentCode>\w+)/(?P<season>[0-9\-]+)/footopia/show-my-leagues$', 'footopia.views_footopia.get_my_leagues', name='f_get_my_leagues'),
    url(r'^(?P<tournamentCode>\w+)/(?P<season>[0-9\-]+)/footopia/create-my-league$', 'footopia.views_footopia.create_new_league', name='f_create_new_league'),
    url(r'^(?P<tournamentCode>\w+)/(?P<season>[0-9\-]+)/footopia/join-league$', 'footopia.views_footopia.join_league', name='f_join_league'),
    url(r'^(?P<tournamentCode>\w+)/(?P<season>[0-9\-]+)/footopia/view-league/(?P<leagueId>\d+)$', 'footopia.views_footopia.view_league', name='f_view_league'),
	# url(r'^(?P<tournamentCode>\w+)/(?P<season>[0-9\-]+)/footopia/show-my-spendings$', 'footopia.views_footopia.show_spendings', name='show_spendings'),
	# url(r'^(?P<tournamentCode>\w+)/(?P<season>[0-9\-]+)/footopia/view-past-footopia-records/(?P<userId>\d+)$', 'footopia.views_footopia.view_past_footopia_records', name='view_past_footopia_records'),
	# url(r'^(?P<tournamentCode>\w+)/(?P<season>[0-9\-]+)/footopia/view-past-teams/(?P<userId>\d+)$', 'footopia.views_footopia.view_past_teams', name='view_past_teams'),
	url(r'^(?P<tournamentCode>\w+)/(?P<season>[0-9\-]+)/footopia/f_rules', 'footopia.views_footopia.rules', name='f_rules'),
	
	# Admin page url action
	#url(r'^adminlogin$', 'django.contrib.auth.views.login', {'template_name':'a_home.html'},name='adminlogin'),
	#url(r'^adminlogout$', 'django.contrib.auth.views.logout_then_login', name='adminlogout'),
	url(r'^admin/somerandomtexttomaketheURLlong$', 'footopia.views_admin.Login', name='admin_login'),
	url(r'^admin/somerandomtexttomaketheURLlong/createTournamentBase$','footopia.views_tournament.createTournamentBase'),
	url(r'^admin/somerandomtexttomaketheURLlong/createTournament$','footopia.views_tournament.createTournament'),
	url(r'^admin/somerandomtexttomaketheURLlong/update_price$','footopia.views_tournament.change_players_price', name='update_price'),
	url(r'^admin/somerandomtexttomaketheURLlong/get_tournament_teams$','footopia.views_tournament.get_tournament_teams', name='get_tournament_teams'),
	url(r'^admin/somerandomtexttomaketheURLlong/get_team_players$','footopia.views_tournament.get_team_players', name='get_team_players'),
	url(r'^admin/somerandomtexttomaketheURLlong/pull_data$','footopia.views_tournament.pull_data',name='pull_data'),

	# url(r'^createGame$','footopia.views_tournament.createGame'),
	url(r'^removeGame$','footopia.views_tournament.removeGame'),
	#url(r'^adminlogin$','footopia.views_admin.login'),

	# D3 charts url
	url(r'^(?P<tournamentCode>\w+)/(?P<season>[0-9\-]+)/get_prediction_chart$','footopia.views_data_server_d3.serve_d3_chart_for_prediction', name='get_prediction_point_statistics'),
	url(r'^(?P<tournamentCode>\w+)/(?P<season>[0-9\-]+)/get_footopia_chart$','footopia.views_data_server_d3.serve_d3_chart_for_footopia', name='get_footopia_point_statistics'),
	
	# Statistics page
	url(r'^(?P<tournamentCode>\w+)/(?P<season>[0-9\-]+)/view-statistics$', 'footopia.views_statistics.home', name='stats_home'),
	url(r'^(?P<tournamentCode>\w+)/(?P<season>[0-9\-]+)/view-statistics/view-top-scorer$', 'footopia.views_statistics.get_top_scorers', name='stats_top_scorers'),
	url(r'^(?P<tournamentCode>\w+)/(?P<season>[0-9\-]+)/view-statistics/view-all-players$', 'footopia.views_statistics.get_all_players', name='stats_all_players'),
	url(r'^(?P<tournamentCode>\w+)/(?P<season>[0-9\-]+)/view-statistics/view-best-players$', 'footopia.views_statistics.get_best_players_of_gameweek', name='stats_best_players'),
	url(r'^(?P<tournamentCode>\w+)/(?P<season>[0-9\-]+)/view-statistics/view-best-team$', 'footopia.views_statistics.get_best_team', name='get_best_team'),

	# Photos
	url(r'^team-logos/(?P<teamId>\d+)$', "footopia.views.get_logos", name="Get_Logos"),
)+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
