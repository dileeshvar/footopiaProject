from django import forms
from django.forms.formsets import BaseFormSet, formset_factory
from django.utils.functional import cached_property

from models import *

class PlayerFilterForm(forms.Form):
	TEAM_CHOICES = (
		('ALL', 'All'),
	)
	PLAYER_TYPE_CHOICES = (
		('ALL', 'All'),
		('GK', 'Goalkeeper'),
		('DF', 'Defender'),
		('MF', 'Midfielder'),
		('ST', 'Striker'),
	)
	team = forms.ChoiceField(choices=TEAM_CHOICES, required=True, label='Team', widget=forms.Select(attrs={
        'class': 'form-control player-filter',
    }))
	player_type = forms.ChoiceField(choices=PLAYER_TYPE_CHOICES, required=True, label='Player Type', widget=forms.Select(attrs={
        'class': 'form-control player-filter',
    }))

	def __init__(self, team_choices=None, *args, **kwargs):
		super(PlayerFilterForm, self).__init__(*args, **kwargs)
		if team_choices:
			self.fields['team'].choices = team_choices
			
class CreateTeamForm(forms.Form):
	gk1 = forms.IntegerField(widget = forms.HiddenInput)
	df1 = forms.IntegerField(widget = forms.HiddenInput)
	df2 = forms.IntegerField(widget = forms.HiddenInput)
	df3 = forms.IntegerField(widget = forms.HiddenInput)
	df4 = forms.IntegerField(widget = forms.HiddenInput)
	mf1 = forms.IntegerField(widget = forms.HiddenInput)
	mf2 = forms.IntegerField(widget = forms.HiddenInput)
	mf3 = forms.IntegerField(widget = forms.HiddenInput)
	mf4 = forms.IntegerField(widget = forms.HiddenInput)
	st1 = forms.IntegerField(widget = forms.HiddenInput)
	st2 = forms.IntegerField(widget = forms.HiddenInput)
	
	def __init__(self, *args, **kwargs):
		self.tourn = kwargs.pop('tourn', None)
		super(CreateTeamForm, self).__init__(*args, **kwargs)
	
	def clean(self):
		cleaned_data = super(CreateTeamForm, self).clean()
		keys = ['gk1', 'df1', 'df2', 'df3', 'df4', 'mf1', 'mf2', 'mf3', 'mf4', 'st1', 'st2']
		player_list = []
		total_cost = 0
		for key in keys:
			player_id = cleaned_data.get(key)
			cost = Squad.get_cost_for_player(self.tourn, player_id)
			if cost == -1: raise forms.ValidationError('Invalid player')
			total_cost = total_cost + cost
			if player_id in player_list:
				raise forms.ValidationError('Two players cannot be the same')
			player_list.append(cleaned_data.get(key))
		if total_cost > 100:
			raise forms.ValidationError('Budget cannot exceed 100')
		return cleaned_data
	
	def clean_gk1(self):
		gk = self.cleaned_data['gk1']
		if not Player.validate(gk, 'GK'):
			raise forms.ValidationError('gk is not a Goalkeeper')
		return gk
	
	def clean_df1(self):
		df = self.cleaned_data['df1']
		if not Player.validate(df, 'DF'):
			raise forms.ValidationError('df1 is not a Defender')
		return df
		
	def clean_df2(self):
		df = self.cleaned_data['df2']
		if not Player.validate(df, 'DF'):
			raise forms.ValidationError('df2 is not a Defender')
		return df
		
	def clean_df3(self):
		df = self.cleaned_data['df3']
		if not Player.validate(df, 'DF'):
			raise forms.ValidationError('df3 is not a Defender')
		return df
		
	def clean_df4(self):
		df = self.cleaned_data['df4']
		if not Player.validate(df, 'DF'):
			raise forms.ValidationError('df4 is not a Defender')
		return df
	
	def clean_mf1(self):
		mf = self.cleaned_data['mf1']
		if not Player.validate(mf, 'MF'):
			raise forms.ValidationError('mf1 is not a Midfielder')
		return mf
		
	def clean_mf2(self):
		mf = self.cleaned_data['mf2']
		if not Player.validate(mf, 'MF'):
			raise forms.ValidationError('mf2 is not a Midfielder')
		return mf
		
	def clean_mf3(self):
		mf = self.cleaned_data['mf3']
		if not Player.validate(mf, 'MF'):
			raise forms.ValidationError('mf3 is not a Midfielder')
		return mf
		
	def clean_mf4(self):
		mf = self.cleaned_data['mf4']
		if not Player.validate(mf, 'MF'):
			raise forms.ValidationError('mf4 is not a Midfielder')
		return mf
		
	def clean_st1(self):
		st = self.cleaned_data['st1']
		if not Player.validate(st, 'ST'):
			raise forms.ValidationError('st1 is not a Striker')
		return st
	
	def clean_st2(self):
		st = self.cleaned_data['st2']
		if not Player.validate(st, 'ST'):
			raise forms.ValidationError('st2 is not a Striker')
		return st
		
class EditTeamForm(forms.Form):
	player_out = forms.IntegerField(widget = forms.HiddenInput)
	player_in = forms.IntegerField(widget = forms.HiddenInput)
	
	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user', None)
		self.tourn = kwargs.pop('tourn', None)
		self.gw = kwargs.pop('gw', None)
		super(EditTeamForm, self).__init__(*args, **kwargs)
		
	def clean(self):
		cleaned_data = super(EditTeamForm, self).clean()
		p1 = cleaned_data.get('player_out')
		p2 = cleaned_data.get('player_in')
		if not p1 or not p2 or not Player.validate_two_players(p1, p2):
			raise forms.ValidationError('Invalid players swapped')
		return cleaned_data
			
	def clean_player_out(self):
		player_out = self.cleaned_data['player_out']
		if not TeamSelection.is_player_in_team(self.tourn, self.gw, self.user, player_out):
			raise forms.ValidationError("Player removed is not in the team")
		return player_out
			
class BaseEditTeamFormSet(BaseFormSet):
	
	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user', None)
		self.tourn = kwargs.pop('tourn', None)
		self.gw = kwargs.pop('gw', None)
		super(BaseEditTeamFormSet, self).__init__(*args, **kwargs)
		
	@cached_property
	def forms(self):
		"""
		Instantiate forms at first property access.
		"""
		forms = [self._construct_form(i, user=self.user, tourn=self.tourn, gw=self.gw) for i in xrange(self.total_form_count())]
		return forms
		
	def clean(self):
		if any(self.errors):
			return
		player_out_list = []
		player_in_list = []
		
		# Validate that no two players are the same
		for form in self.forms:
			player_out = form.cleaned_data['player_out']
			player_in = form.cleaned_data['player_in']
			if player_out == player_in:
				raise forms.ValidationError('Cannot swap player with himself')
			if player_out in player_in_list:
				raise forms.ValidationError('Cannot swap player with himself')
			if player_out in player_out_list or player_in in player_in_list:
				raise forms.ValidationError('Two players cannot be the same')
			player_out_list.append(player_out)
			player_in_list.append(player_in)
			
EditTeamFormSet = formset_factory(EditTeamForm, formset=BaseEditTeamFormSet, max_num=11, validate_max=True, min_num=1, validate_min=True, extra=11)

class EditTeamMetaForm(forms.Form):
	use_wildcard = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={'id':'useWildcardId'}))
	
	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user', None)
		self.tourn = kwargs.pop('tourn', None)
		self.transfers = kwargs.pop('transfers', 0)
		super(EditTeamMetaForm, self).__init__(*args, **kwargs)
		
	def clean(self):
		cleaned_data = super(EditTeamMetaForm, self).clean()
		if not cleaned_data.get('use_wildcard') and not UserEnrollmentFootopia.is_transfers_remaining(self.tourn, self.user, self.transfers):
			raise forms.ValidationError('Not enough transfers remaining')
		if cleaned_data.get('use_wildcard') and not UserEnrollmentFootopia.is_wildcard_remaining(self.tourn, self.user):
			raise forms.ValidationError('Cannot use wildcard as all wildcards are already used')
		
		