from django import forms
from footopia.models import *
from django.contrib.auth.models import User

class RegistrationForm(forms.Form):
	username = forms.CharField(max_length = 20, label='username', widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'User name'}))

	firstName = forms.CharField(max_length = 20, label='Your name', widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'First Name'}))

	lastName = forms.CharField(max_length = 20,
	widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Last Name'}))

	email = forms.EmailField(max_length = 100,
	widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'email address'}))

	password1 = forms.CharField(max_length = 200,
	widget = forms.PasswordInput(attrs={'class':'form-control', 'placeholder': 'Password'}))
	password2 = forms.CharField(max_length = 200,
	widget = forms.PasswordInput(attrs={'class':'form-control', 'placeholder': 'Confirm Password'}))

	country = forms.ModelChoiceField(queryset=Country.objects.all().order_by("country"),required = False,
	empty_label="Fav Country",  widget=forms.Select(attrs={'class':'form-control'}))

	club = forms.ModelChoiceField(queryset=Club.objects.all().order_by("club_name"),required = False,
	empty_label="Fav Club", widget=forms.Select(attrs={'class':'form-control'}))

	player = forms.ModelChoiceField(queryset=Player.objects.all().order_by("player_name"),required = False, empty_label="Fav Player", widget=forms.Select(attrs={'class':'form-control'}))
    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
	def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
		cleaned_data = super(RegistrationForm, self).clean()

        # Confirms that the two password fields match
		username = cleaned_data.get('username')
		firstName = cleaned_data.get('firstName')
		lastName = cleaned_data.get('lastName')
		email = cleaned_data.get('email')
		password1 = cleaned_data.get('password1')
		password2 = cleaned_data.get('password2')
		country = cleaned_data.get('country')
		club = cleaned_data.get('club')
		player = cleaned_data.get('player')
		if password1 and password2 and password1 != password2:
			raise forms.ValidationError("Passwords did not match.")

        # Generally return the cleaned data we got from our parent.
		return cleaned_data

    # Customizes form validation for the username field.
	def clean_username(self):
        # Confirms that the username is not already present in the
        # User model database.
		username = self.cleaned_data.get('username')
		if User.objects.filter(username__exact=username):
			raise forms.ValidationError("Username is already taken.")

        # Generally return the cleaned data we got from the cleaned_data
        # dictionary
		return username

	def clean_email(self):
		# Confirms that the username is not already present in the
		# User model database.
		email = self.cleaned_data.get('email')
		if User.objects.filter(email__exact=email):
			raise forms.ValidationError("email is already taken.")

		# Generally return the cleaned data we got from the cleaned_data
		# dictionary
		return email

class ResetForm(forms.Form):
	email = forms.EmailField(max_length = 100,
	widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'email address'}))

	def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
		cleaned_data = super(ResetForm, self).clean()

        # Confirms that the two password fields match
		email = cleaned_data.get('email')

        # Generally return the cleaned data we got from our parent.
		return cleaned_data

    # Customizes form validation for the username field.
	def clean_email(self):
        # Confirms that the username is not already present in the
        # User model database.
		email = self.cleaned_data.get('email')
		if User.objects.filter(email__exact=email):
			return email
		else:
			raise forms.ValidationError("Sorry !! Email id not registered")

        # Generally return the cleaned data we got from the cleaned_data
        # dictionary

class ResetPasswordForm(forms.Form):
	password1 = forms.CharField(max_length = 200,
	widget = forms.PasswordInput(attrs={'class':'form-control', 'placeholder': 'Password'}))
	password2 = forms.CharField(max_length = 200,
	widget = forms.PasswordInput(attrs={'class':'form-control', 'placeholder': 'Confirm Password'}))

	def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
		cleaned_data = super(ResetPasswordForm, self).clean()

        # Confirms that the two password fields match
		password1 = cleaned_data.get('password1')
		password2 = cleaned_data.get('password2')
        # Generally return the cleaned data we got from our parent.

		if password1 and password2 and password1 != password2:
			raise forms.ValidationError("Passwords did not match.")

        # Generally return the cleaned data we got from our parent.
		return cleaned_data
