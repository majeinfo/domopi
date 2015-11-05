from django.utils.translation import ugettext as _
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from . models import Command, Sensor, Controller
import json


@login_required
def indexAction(request, key):

    sensors = Sensor.objects.filter(key=key)
    context = {
        'sensors': sensors,
    }
    return render(request, 'sensors/index.html', context)


# Send (Log) a command to a Device
# TODO: check the Controller belongs to the User
@login_required
def commandAction(request, key, zid, sid, cmd):

    if not _checkOwner(request, key, zid, sid):
        messages.error(request, _('Invalid Parameters'))
        return redirect('controllers_index')

    cmd = Command.objects.create(
        key = key,
        zid = zid,
        sid = sid,
        cmd = json.dumps({ 'cmd': cmd })
    )
    cmd.save()
    messages.info(request, 'Command Sent - please wait 10 seconds before changes apply')
    return HttpResponseRedirect('/frontend/sensors/' + key)


#Change a sensor title (name)
@login_required
def setdescrAction(request, key, zid, sid):

    if request.method == 'POST':
        sensor = _checkOwner(request, key, zid, sid)
        if not sensor:
            messages.error(request, _('Invalid Parameters'))
            return redirect('controllers_index')

        newdescr = request.POST['newname']
        if newdescr:
            cmd = Command.objects.create(
                key = key,
                zid = zid,
                sid = sid,
                cmd = json.dumps({ 'cmd': 'setdescr', 'value': newdescr })
            )
            cmd.save()
            sensor.description = newdescr
            sensor.save()
            messages.info(request, 'Command Sent - please wait 10 seconds before changes apply')

    return HttpResponseRedirect('/frontend/sensors/' + key)


# Check the User towards the key/zid/sid
def _checkOwner(request, key, zid, sid=None):
    try:
        controller = Controller.objects.get(login=request.user.username, key=key, zid=zid)
    except:
        return None

    if not sid: return controller

    try:
        sensor = Sensor.objects.get(key=key, sid=sid)
    except:
        return None

    return sensor
