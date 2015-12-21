from django.utils.translation import ugettext as _
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User as DjangoUser
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib import messages
from . forms import LoginForm, SubscribeForm
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
                try:
                    user = User.objects.get(login=n)
                    tz = user.timezone if user.timezone else 'UTC'
                    timezone.activate(tz)
                    request.session['django_timezone'] = tz
                    messages.info(request, _('Authentication successfull'))
                    return HttpResponseRedirect('/frontend/controllers')
                except Exception as e:
                    messages.error(request, _('Authentication failed - internal error, please contact the Technical Support'))
                    #messages.error(request, e)
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


def subscribeAction(request):
    if request.method == 'POST':
        form = SubscribeForm(request.POST)
        if form.is_valid():
            n = form.cleaned_data['username']
            p = form.cleaned_data['password']
            p2 = form.cleaned_data['password2']
            e = form.cleaned_data['email']

            # Consistency checks :
            # username must be unique
            # passwords must match
            if p != p2:
                messages.error(request, _('Passwords mismatch, please enter your Password again'))
            try:
                user = User.objects.get(login=n)
                messages.error(request, _('This Username already exists, please choose another one !'))
            except:
                # Create User in Django Auth System and MongoDB
                dj_user = DjangoUser.objects.create_user(n, e, p)
                dj_user = authenticate(username=n, password=p, request=request)
                user = User()
                user.login = n
                user.email = e
                user.password = p
                user.save()
                login(request, dj_user)
                messages.info(request, _('Your Account has been created succesfully ! We recommend you to complete your Profile'))
                request.session['django_timezone'] = 'UTC'
                return HttpResponseRedirect('/frontend/controllers')
        else:
            messages.error(request, _('Invalid Form Values'))
    else:
        form = SubscribeForm()

    return render(request, 'auth/subscribe.html', { 'form': form })



