from django.utils.translation import ugettext as _
from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(max_length=75, label=_('Your Login'))
    password = forms.CharField(widget=forms.PasswordInput, label=_('Your Password'))


class AddDeviceForm(forms.Form):
    key = forms.CharField(max_length=80, label=_('Controller ID'), help_text=_('This is the value written on you Domopi Box'))
