from django.utils.translation import ugettext as _
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from . models import Controller
from . forms import AddDeviceForm


# Must display the devices owned by the user
@login_required
def indexAction(request):
    controllers = Controller.objects.filter(login=request.user.username)
    context = {
        'controllers': controllers,
    }
    return render(request, 'controllers/index.html', context)


# Add a device for the User
@login_required
def addAction(request):
    if request.method == 'POST':
        form = AddDeviceForm(request.POST)
        if form.is_valid():
            key = form.cleaned_data['key']
            try:
                controller = Controller.objects.get(key=key)
            except:
                controller = None
            if not controller or controller.login:
                # TODO: check the Controller is not associated to someone else
                messages.error(request, _('The Controller ID is invalid')) # or is already associated
            else:
                controller.login = request.user.username
                controller.save()
                messages.info(request, _('The Controller has been attached to your Account'))
                return HttpResponseRedirect('/frontend/controllers')
        else:
            messages.error(request, _('Invalid Form Values'))
    else:
        form = AddDeviceForm()

    return render(request, 'controllers/add.html', { 'form': form })


# Delete a Controller from User Account
# TODO: check the Controller belongs to the User
@login_required
def deleteAction(request, key):
    return render(request, 'controllers/index.html', {})


# Add a User's Description to a Controller
# TODO: check the Controller belongs to the User
@login_required
def setDescriptionAction(request, key):
    return render(request, 'controllers/index.html', {})

