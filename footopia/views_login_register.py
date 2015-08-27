from django.shortcuts import redirect,render,get_object_or_404
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth import login,authenticate
from footopia.models import *
from footopia.forms_register import *
from django.core.urlresolvers import reverse
# Used to generate a one-time-use token to verify a user's email address
from django.contrib.auth.tokens import default_token_generator
# Used to send mail from within Django
from django.core.mail import send_mail

def register(request):
	context = {}
    # Just display the registration form if this is a GET request.
	if request.method == 'GET':
		context['R_form'] = RegistrationForm()
		context['Reset_form'] = ResetForm()
		return render(request, 'home.html', context)
	form = RegistrationForm(request.POST)
	context['R_form'] = form
	context['Reset_form'] = ResetForm()
    # Validates the form.
	if not form.is_valid():
		return render(request, 'home.html', context)

    # If we get here the form data was valid.  Register and login the user.
	new_user = User.objects.create_user(username=form.cleaned_data['username'],
		password=form.cleaned_data['password1'],
		first_name=form.cleaned_data['firstName'],
		last_name=form.cleaned_data['lastName'],
		email=form.cleaned_data['email'])
	new_user.is_active = False
	new_user.save()

	country =  form.cleaned_data['country']
	club = form.cleaned_data['club']
	player = form.cleaned_data['player']
	new_user_details = UserProfile(fav_country = country,
	fav_club = club, user = new_user, fav_player=player)
	new_user_details.save()

    # Generate a one-time use token and an email message body
	token = default_token_generator.make_token(new_user)

	email_body = """
Welcome to the Footopia.  Please click the link below to
verify your email address and complete the registration of your account:

  http://%s%s
""" % (request.get_host(), 
		reverse('confirm', args=(new_user.username, token)))		
	send_mail(subject="Footopia - Registration",
		message= email_body,
		from_email="no-reply@footopia.com",
		recipient_list=[new_user.email]) 
		
	context['email'] = new_user.email
	context['initiator'] = 'Registration'
    
	return render(request, 'u_confirmation.html', context)
    	
def confirm_registration(request, username, token):
	context={}
	user = get_object_or_404(User, username=username)

    # Send 404 error if token is invalid
	if not default_token_generator.check_token(user, token):
		raise Http404

    # Otherwise token was valid, activate the user.
	user.is_active = True
	user.save()
	
	context['confirmStatus'] = 'true'
	context['passwordChangeStatus'] = 'false'
	
	return render(request, 'u_confirmed.html', context)
	
def reset(request):
	context = {}
    # Just display the registration form if this is a GET request.
	if request.method == 'GET':
		context['R_form'] = RegistrationForm()
		context['Reset_form'] = ResetForm()
		return render(request, 'home.html', context)
	form = ResetForm(request.POST)
	context['Reset_form'] = form
	context['R_form'] = RegistrationForm()
    # Validates the form.
	if not form.is_valid():
		return render(request, 'home.html', context)

	email = form.cleaned_data['email']	    
	
	registeredUser = User.objects.get(email__exact=email)
    # Generate a one-time use token and an email message body
	token = default_token_generator.make_token(registeredUser)

	email_body = """

Welcome to the Footopia.  Please click the link below to
reset the password

  http://%s%s
""" % (request.get_host(), 
		reverse('reset', args=(registeredUser.username, token)))		
	send_mail(subject="Footopia - Reset your password",
		message= email_body,
		from_email="no-reply@footopia.com",
		recipient_list=[email])
	
	context['registeredUser'] = registeredUser
	context['email'] = email	
	context['initiator'] = 'Reset'
    
	return render(request, 'u_confirmation.html', context)
	
def reset_password(request, username, token):
	context = {}
	user = get_object_or_404(User, username=username)

    # Send 404 error if token is invalid
	if not default_token_generator.check_token(user, token):
		raise Http404
    
	context['Reset_Password_form'] = ResetPasswordForm()
	
	return render(request, 'u_confirmed.html', context)
	
def resetDone(request, username):
	context = {}	
	form = ResetPasswordForm(request.POST)
	context['Reset_Password_form'] = form
	if not form.is_valid():
		return render(request, 'u_confirmed.html', context)
	
	user = get_object_or_404(User, username=username)	
	user.set_password(form.cleaned_data['password1'])	
	user.save()
	
	context['confirmStatus'] = 'true'
	context['passwordChangeStatus'] = 'true'
	
	return render(request, 'u_confirmed.html', context)