from django.utils.translation import ugettext as _
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib import messages
from . forms import LoginForm
from . models import User


def loginAction(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            n = form.cleaned_data['username']
            p = form.cleaned_data['password']
            user = authenticate(username=n, password=p, request=request)
            if user is not None:
                login(request, user)
                messages.info(request, _('Authentication successfull'))
                user = User.objects.get(login=n)
                timezone.activate(user.timezone)
                request.session['django_timezone'] = user.timezone if user.timezone else 'UTC'
                return HttpResponseRedirect('/frontend/controllers')
            else:
                messages.error(request, _('Authentication failed - either your Login or your Password is incorrect'))
        else:
            messages.error(request, _('Invalid Form Values'))
    else:
        form = LoginForm()

    return render(request, 'auth/login.html', { 'form': form })


def logoutAction(request):
    logout(request)
    return HttpResponseRedirect('/frontend')



