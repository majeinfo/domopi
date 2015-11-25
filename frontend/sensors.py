from django.utils.translation import ugettext as _
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from . models import Command, Sensor, checkSensorOwner
import json
import collections


@login_required
def indexAction(request, key):

    sensors = Sensor.objects.filter(key=key).order_by('devid', 'instid')

    # Let's try to prepare a Tree instead of a List
    tree = collections.OrderedDict()
    for sensor in sensors:
        if not sensor.devid in tree: tree[sensor.devid] = { 'has_battery': None }
        if not sensor.instid in tree[sensor.devid]: tree[sensor.devid][sensor.instid] = collections.OrderedDict()
        tree[sensor.devid][sensor.instid][sensor.sid] = sensor
        sensor.is_temperature = sensor.metrics.probeTitle and sensor.metrics.probeTitle.lower().startswith('temperature')
        sensor.is_light = sensor.metrics.probeTitle and sensor.metrics.probeTitle.lower().startswith('luminiscence')
        sensor.is_door = sensor.metrics.probeTitle and sensor.metrics.probeTitle.lower().startswith('door')
        sensor.is_motion = sensor.metrics.probeTitle and sensor.metrics.probeTitle.lower().startswith('motion')
        sensor.is_tamper = sensor.metrics.probeTitle and sensor.metrics.probeTitle.lower().startswith('tamper')
        sensor.is_alarm = sensor.devtype.lower().startswith('sensor')

    # Try to attache Battery sensors to their root Device
    for sensor in sensors:
        if sensor.devtype.lower() == 'battery':
            tree[sensor.devid]['has_battery'] = int(sensor.metrics.level)
            sensor.is_battery = True

    context = {
        'key': key,
        'sensors': sensors,
        'tree': tree,
    }
    return render(request, 'sensors/index.html', context)


# Send (Log) a command to a Device
@login_required
def commandAction(request, key, zid, devid, instid, sid, cmd):

    if not checkSensorOwner(request.user.username, key, zid):
        messages.error(request, _('Invalid Parameters'))
        return redirect('controllers_index')

    cmd = Command.objects.create(
        key = key,
        zid = zid,
        cmd = cmd,
        parms = json.dumps({ 'devid': devid, 'instid': instid, 'sid': sid })
    )
    cmd.save()
    messages.info(request, 'Command Sent - please wait 10 seconds before changes apply')
    return HttpResponseRedirect('/frontend/sensors/' + key)


#Change a sensor title (name)
@login_required
def setdescrAction(request, key, zid, devid, instid, sid):

    if request.method == 'POST':
        sensor = checkSensorOwner(request.user.username, key, zid, sid)
        if not sensor:
            messages.error(request, _('Invalid Parameters'))
            return redirect('controllers_index')

        newdescr = request.POST['newname']    # TODO: check injection
        if newdescr:
            cmd = Command.objects.create(
                key = key,
                zid = zid,
                cmd = 'sensor_setdescr',
                parms = json.dumps({ 'devid': devid, 'instid': instid, 'sid': sid, 'value': newdescr })
            )
            cmd.save()
            sensor.description = newdescr
            sensor.save()
            messages.info(request, 'Command Sent - please wait 10 seconds before changes apply')

    return HttpResponseRedirect('/frontend/sensors/' + key)


