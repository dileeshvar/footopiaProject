from django import forms
from models import *

class GetFixturesForm(forms.Form):
	gameweek = forms.IntegerField()
	
class PredictionForm(forms.Form):
	match = forms.CharField()
	team1_score = forms.IntegerField(required = False)
	team2_score = forms.IntegerField(required = False)
	'''class Meta:
		model = UserPrediction
		fields = ('match', 'team1_score', 'team2_score')'''
	
	def clean(self):
		cleaned_data = super(PredictionForm, self).clean()
		if (cleaned_data.get('team1_score') == None and not cleaned_data.get('team2_score') == None) or (cleaned_data.get('team2_score') == None and not cleaned_data.get('team1_score') == None):
			raise forms.ValidationError('Enter score for both teams')
		return cleaned_data
		
	def clean_team1_score(self):
		if not self.cleaned_data.get('team1_score') == None and self.cleaned_data.get('team1_score') < 0:
			raise forms.ValidationError('Enter valid score for team 1')
		return self.cleaned_data.get('team1_score')
		
	def clean_team2_score(self):
		if not self.cleaned_data.get('team2_score') == None and self.cleaned_data.get('team2_score') < 0:
			raise forms.ValidationError('Enter valid score for team 2')
		return self.cleaned_data.get('team2_score')