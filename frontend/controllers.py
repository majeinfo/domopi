from django.utils.translation import ugettext as _
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import json
from . models import Controller, Command, Log, checkControllerOwner
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
            # check the Controller exists and is not associated to someone else
            if not controller or controller.login:
                messages.error(request, _('The Controller ID is invalid')) # or is already associated
            else:
                controller.login = request.user.username
                controller.save()
                messages.info(request, _('The Controller has been attached to your Account'))
                return redirect('controllers_index')
        else:
            messages.error(request, _('Invalid Form Values'))
    else:
        form = AddDeviceForm()

    return render(request, 'controllers/add.html', { 'form': form })


# Delete a Controller from User Account
@login_required
def deleteAction(request, key):
    controller = checkControllerOwner(request.user.username, key)
    if not controller:
        messages.error(request, _('Invalid Parameters'))
    else:
        controller.login = None
        controller.save()
        messages.info(request, _('The Controller has been removed from your Account'))

    return redirect('controllers_index')


# Add a User's Description to a Controller
@login_required
def setDescriptionAction(request, key):
    if request.method == 'POST':
        controller = checkControllerOwner(request.user.username, key)
        if not controller:
            messages.error(request, _('Invalid Parameters'))
            return redirect('controllers_index')

        newdescr = request.POST['newdescr']  # TODO: check injection
        if newdescr:
            controller.description = newdescr
            controller.save()
            cmd = Command.objects.create(
                key = key,
                zid = controller.zid,
                cmd = 'controller_setdescr',
                parms = json.dumps({ 'value': newdescr })
            )
            cmd.save()
            messages.info(request, 'Command Sent - please wait 10 seconds before changes apply')

    return redirect('controllers_index')


# Get the last logs of remote Controller
@login_required
def viewLogs(request, key):
    controller = checkControllerOwner(request.user.username, key)
    if not controller:
        messages.error(request, _('Invalid Parameters'))
    else:
        logs = Log.objects.filter(key=key).order_by('-date')
        cmd = Command.objects.create(
            key = key,
            zid = controller.zid,
            cmd = 'controller_getlogs',
            parms = json.dumps({ 'value': '' })
        )
        cmd.save()
        messages.info(request, _('The Controller will send the Logs...'))
        return render(request, 'controllers/viewlogs.html', { 'logs': logs })

    return redirect('controllers_index')
