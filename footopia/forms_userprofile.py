from django import forms

from models import *
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm

class ProfileForm(forms.Form):
	prof_firstname = forms.CharField(max_length = 30, label='First Name',
								widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'First Name'}))
	prof_lastname = forms.CharField(max_length = 30, label='Last Name',
								widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Last Name'}))
	prof_email = forms.CharField(max_length = 50, label='Email',
								widget=forms.EmailInput(attrs={'class':'form-control', 'placeholder': 'Email'}))
	prof_favorite_country = forms.ModelChoiceField(queryset=Country.objects.all().order_by('country'), widget=forms.Select(attrs={'class':'form-control'}), label='Favorite Country')
	prof_favorite_team = forms.ModelChoiceField(queryset=Club.objects.all().order_by('club_name'), widget=forms.Select(attrs={'class':'form-control'}), label='Favorite Team')
	prof_favorite_player = forms.ModelChoiceField(queryset=Player.objects.all().order_by('player_name'), widget=forms.Select(attrs={'class':'form-control'}), label='Favorite Player')

	def clean_prof_firstname(self):
		prof_firstname = self.cleaned_data.get('prof_firstname')
		if not prof_firstname:
			raise forms.ValidationError("First name is required.(DOT)")
		return prof_firstname

	def clean_prof_lastname(self):
		prof_lastname = self.cleaned_data.get('prof_lastname')
		if not prof_lastname:
			raise forms.ValidationError("Last name is required.(DOT)")
		return prof_lastname

	def clean_prof_email(self):
		prof_email = self.cleaned_data.get('prof_email')
		if not prof_email:
			raise forms.ValidationError("Email is required.(DOT)")
		return prof_email
