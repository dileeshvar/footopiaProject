from django import forms
from django.contrib.auth.models import User
from models import *
from model_utils import *

class TournamentBaseForm(forms.ModelForm):
	class Meta:
		model = TournamentBase
		fields = ['tourn_cd','tourn_name','tourn_desc','country','tournament_type']
		
class CreateTournamentForm(forms.Form):
	season = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),label='Enter Season', max_length=7)
	transfer = forms.IntegerField(widget=forms.TextInput(attrs={'class':'form-control'}),label='Enter transfers possible')
	wildcard = forms.IntegerField(widget=forms.TextInput(attrs={'class':'form-control'}),label='Enter wildcards possible')
	
	def clean_season(self):
		season = self.cleaned_data.get('season')
		if not season:
			raise forms.ValidationError("Season is required.(DOT)")
		return season
	
	def clean_transfer(self):
		transfer = self.cleaned_data.get('transfer')
		if not transfer:
			raise forms.ValidationError("transfer is required.(DOT)")
		return transfer
		
	def clean_wildcard(self):
		wildcard = self.cleaned_data.get('wildcard')
		if not wildcard:
			raise forms.ValidationError("wildcard is required.(DOT)")
		return wildcard
	
class EnrollmentForm(forms.Form):
	TEAM_CHOICES = (
		(-1, 'None'),
	)
	team = forms.ChoiceField(choices=TEAM_CHOICES, required=True, label='Favorite Team', widget=forms.Select(attrs={
        'class': 'form-control',
    }))
	def __init__(self, tourn, *args, **kwargs):
		super(EnrollmentForm, self).__init__(*args, **kwargs)
		team_choices = get_team_choices_for_tourn(tourn, include_all = False)
		self.fields['team'].choices = team_choices
		
class MatchInfoIdForm(forms.Form):
	match_id = forms.IntegerField()