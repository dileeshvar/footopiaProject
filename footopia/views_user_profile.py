from footopia.models import *
from footopia.forms_userprofile import *
from django.shortcuts import render, get_object_or_404

def show_profile(request, userId):
	context = {}
	if request.method == "GET":
		user = get_object_or_404(User, id=userId)
		profile = ProfileForm(initial={ "prof_firstname": user.first_name, "prof_lastname": user.last_name, "prof_email": user.email, "prof_favorite_country": user.userprofile.fav_country, "prof_favorite_team":user.userprofile.fav_club, "prof_favorite_player":user.userprofile.fav_player})
		if int(request.user.id) != int(userId):
			profile.fields['prof_firstname'].widget.attrs['disabled'] = True
			profile.fields['prof_lastname'].widget.attrs['disabled'] = True
			profile.fields['prof_email'].widget.attrs['disabled'] = True
			profile.fields['prof_favorite_country'].widget.attrs['disabled'] = True
			profile.fields['prof_favorite_team'].widget.attrs['disabled'] = True
			profile.fields['prof_favorite_player'].widget.attrs['disabled'] = True
			context["is_me"] = False
		else:
			context["is_me"] = True
		context["Profile_Form"] = profile
	else:
		profile = ProfileForm(request.POST)
		user = get_object_or_404(User, id=userId)
		if not profile.is_valid():
			context["Profile_Form"] = profile
			context["is_me"] = True
			return render(request, "u_profile.html", context)
		user.first_name = request.POST["prof_firstname"]
		user.last_name = request.POST["prof_lastname"]
		user.email = request.POST["prof_email"]
		user.userprofile.fav_country = Country.objects.get(country_cd_id = request.POST["prof_favorite_country"])
		user.userprofile.fav_club = Club.objects.get(club_cd_id = request.POST["prof_favorite_team"])
		user.userprofile.fav_player = Player.objects.get(id=request.POST["prof_favorite_player"])
		user.save()
		user.userprofile.save()
		profile = ProfileForm(initial={ "prof_firstname": user.first_name, "prof_lastname": user.last_name, "prof_email": user.email, "prof_favorite_country": user.userprofile.fav_country, "prof_favorite_team":user.userprofile.fav_club, "prof_favorite_player":user.userprofile.fav_player})
		context["Profile_Form"] = profile
		context["status"] = "success"
		context["is_me"] = True
	my_enrollements = UserEnrollment.objects.filter(user=user)
	tournaments = []
	for enroll in my_enrollements:
		tourn = enroll.game.tourn
		if tourn not in tournaments:
			tournaments.append(tourn)
	context["tournaments"] = tournaments
	return render(request, "u_profile.html", context)		