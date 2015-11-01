from django.utils.translation import ugettext as _
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from . models import Command, Sensor


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
def commandAction(request, key, sid, cmd):
    try:
        sensor = Sensor.objects.get(key=key, sid=sid)
    except:
        messages.error(request, _('Invalid Parameters'))
        return redirect('controllers_index')

    cmd = Command.objects.create(
        key = key,
        zid = sensor.zid,
        sid = sid,
        cmd = cmd
    )
    cmd.save()
    messages.info(request, 'Command Sent - please wait 10 seconds before changes apply')
    return HttpResponseRedirect('/frontend/sensors/' + key)


