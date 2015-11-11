from django.utils.translation import ugettext as _
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from . models import Command, Sensor, Controller
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
        'sensors': sensors,
        'tree': tree,
    }
    return render(request, 'sensors/index.html', context)


# Send (Log) a command to a Device
@login_required
def commandAction(request, key, zid, devid, instid, sid, cmd):

    if not _checkOwner(request, key, zid):
        messages.error(request, _('Invalid Parameters'))
        return redirect('controllers_index')

    cmd = Command.objects.create(
        key = key,
        zid = zid,
        devid = devid,
        instid = instid,
        sid = sid,
        cmd = json.dumps({ 'cmd': cmd })
    )
    cmd.save()
    messages.info(request, 'Command Sent - please wait 10 seconds before changes apply')
    return HttpResponseRedirect('/frontend/sensors/' + key)


#Change a sensor title (name)
@login_required
def setdescrAction(request, key, zid, devid, instid, sid):

    if request.method == 'POST':
        sensor = _checkOwner(request, key, zid, sid)
        if not sensor:
            messages.error(request, _('Invalid Parameters'))
            return redirect('controllers_index')

        newdescr = request.POST['newname']    # TODO: check injection
        if newdescr:
            cmd = Command.objects.create(
                key = key,
                zid = zid,
                devid = devid,
                instid = instid,
                sid = sid,
                cmd = json.dumps({ 'cmd': 'setdescr', 'value': newdescr })
            )
            cmd.save()
            sensor.description = newdescr
            sensor.save()
            messages.info(request, 'Command Sent - please wait 10 seconds before changes apply')

    return HttpResponseRedirect('/frontend/sensors/' + key)


# Check the User towards the key/zid/sid
def _checkOwner(request, key, zid, devid=None, instid=None, sid=None):
    try:
        controller = Controller.objects.get(login=request.user.username, key=key, zid=zid)
    except:
        return None

    if not devid or not instid or not sid: return controller

    try:
        sensor = Sensor.objects.get(key=key, devid=devid, instid=instid, sid=sid)
    except:
        return None

    return sensor
