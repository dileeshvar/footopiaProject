from django import forms
from models import *
import re
from django.core import validators
from django.forms import CharField, Textarea, ValidationError
from django.utils.translation import ugettext as _
email_separator_re = re.compile(r'[,;]+')


def _is_valid_email(email):
    try:
        validators.validate_email(email)
        return True
    except forms.ValidationError:
        return False

class EmailsListField(CharField):
    widget = Textarea
    def clean(self, value):
        super(EmailsListField, self).clean(value)
        emails = email_separator_re.split(value)
        if not emails:
            raise ValidationError(_(u'Enter at least one e-mail address.'))
        for email in emails:
            if not _is_valid_email(email.strip()):
                raise ValidationError(_('%s is not a valid e-mail address.') % email)
        return emails

class CreateLeagueForm(forms.Form):
    name = forms.CharField(max_length = 30, label='League Name',
        widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'League Name'}))
    description = forms.CharField(max_length = 200, label='League Description',
        widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Description'}))
    email_ids = EmailsListField(label='Invite Members',
    widget=forms.Textarea(attrs={'class':'form-control','placeholder': 'Enter Email address seperated by comma', 'cols': 30, 'rows': 10}))

    def clean(self):
        cleaned_data = super(CreateLeagueForm, self).clean()
        name = cleaned_data.get('name')
        description = cleaned_data.get('description')
        email_ids = cleaned_data.get('email_ids')
        return cleaned_data

class JoinLeagueForm(forms.Form):
    uniquecode = forms.CharField(max_length = 30, label='Enter League Unique Code',
        widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'UniqueCode'}))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.tourn = kwargs.pop('tourn', None)
        self.g_type = kwargs.pop('gt', None)
        self.season = kwargs.pop('season', None)
        super(JoinLeagueForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(JoinLeagueForm, self).clean()
        uniqueCode = cleaned_data.get('uniqueCode')
        return cleaned_data

    def clean_uniquecode(self):
        uniquecode = self.cleaned_data.get('uniquecode')
        if not GameLeague.objects.filter(uniqueCode__exact=uniquecode):
            raise forms.ValidationError("Invalid UniqueCode")
        if not GameLeague.isValidCode(uniquecode, self.tourn, self.season, self.g_type):
            raise forms.ValidationError("UniqueCode does not match this tournament or game type")
        if GameLeague.isUserExist(self.user, uniquecode):
            raise forms.ValidationError("You have already joined this league")
        return uniquecode
