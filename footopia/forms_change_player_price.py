from django import forms
import datetime
from models import *

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

def getOrgUnitList():		
		TOURNS = []
		TOURNS.extend([(-1, "----")] + [(t.id, t.tourn_name) for t in Tournament.objects.filter(season=find_season()).order_by('tourn_name')])
		return TOURNS

class PlayerPriceForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(PlayerPriceForm, self).__init__(*args, **kwargs)
		self.fields['tournament'].choices = getOrgUnitList()

	TOURNS = getOrgUnitList()
	PRICES = [(i,i) for i in range(1,21)]
	
	tournament = forms.ChoiceField(choices = TOURNS, widget=forms.Select(attrs={'class':'form-control','id':'selTourn'}), label='Select Tournament')
	team = forms.CharField(widget=forms.Select(attrs={'class':'form-control','id':'selTeam'}), label='Select Team')
	player = forms.CharField(widget=forms.Select(attrs={'class':'form-control','id':'selPlayer'}), label='Select Player')
	price = forms.ChoiceField(choices = PRICES, label="New Price")
	
	def clean_team(self):
		team = self.cleaned_data.get('team')
		if not team or team == -1:
			raise forms.ValidationError("Team` is required.(DOT)")
		return team
	
	def clean_tournament(self):
		tournament = self.cleaned_data.get('tournament')
		if not tournament or tournament == str(-1):
			raise forms.ValidationError("Tournament is required.(DOT)")
		return tournament
	
	def clean_player(self):
		player = self.cleaned_data.get('player')
		if not player or player == -1:
			raise forms.ValidationError("Player is required.(DOT)")
		return player
	
	def clean_price(self):
		price = self.cleaned_data.get('price')
		if not price:
			raise forms.ValidationError("Price is required.(DOT)")
		return price
		
class GetDataForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(GetDataForm, self).__init__(*args, **kwargs)
		self.fields['tournament'].choices = getOrgUnitList()

	TOURNS = getOrgUnitList()
	tournament = forms.ChoiceField(choices = TOURNS, widget=forms.Select(attrs={'class':'form-control','id':'getDataTourn',}), label='Select Tournament')