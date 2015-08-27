from django import forms
from django.contrib.auth.models import User

class AdminLogin(forms.Form):
	username = forms.CharField(max_length=20,required=True,widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'username'}))
	password = forms.CharField(max_length=8,required=True,widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'password'}))
	
	def clean(self):
		cleaned_data = super(AdminLogin, self).clean()
		username = cleaned_data.get('username')
		password = cleaned_data.get('password')
		return cleaned_data

	# Customizes form validation for the username field.
	def clean_username(self):
		username = self.cleaned_data.get('username')
		if username == '':
			raise forms.ValidationError("Username must be entered.")
		if User.objects.filter(username__exact=username):
			raise forms.ValidationError("Username is already taken.")	
		return username
	def clean_password(self):
		password = self.cleaned_data.get('password')
		if password == '':
			raise forms.ValidationError("Password must be entered.")
		return password