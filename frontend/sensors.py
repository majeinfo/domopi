import logging
from django.utils.translation import ugettext as _
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from . models import Command, Sensor, checkSensorOwner
import json
import collections

logger = logging.getLogger('domopi')

@login_required
def indexAction(request, key):

    sensors = Sensor.objects.filter(key=key).order_by('devid', 'instid')

    # Let's try to prepare a Tree instead of a List
    tree = collections.OrderedDict()
    for sensor in sensors:
        if not sensor.devid in tree: tree[sensor.devid] = { 'has_battery': None, 'has_hidden': False, 'key': sensor.key, 'zid': sensor.zid }
        if not sensor.instid in tree[sensor.devid]: tree[sensor.devid][sensor.instid] = collections.OrderedDict()
        tree[sensor.devid][sensor.instid][sensor.sid] = sensor
        sensor.is_temperature = sensor.metrics.probeTitle and sensor.metrics.probeTitle.lower().startswith('temperature')
        sensor.is_light = sensor.metrics.probeTitle and sensor.metrics.probeTitle.lower().startswith('luminiscence')
        sensor.is_door = sensor.metrics.probeTitle and sensor.metrics.probeTitle.lower().startswith('door')
        sensor.is_motion = sensor.metrics.probeTitle and sensor.metrics.probeTitle.lower().startswith('motion')
        sensor.is_tamper = sensor.metrics.probeTitle and sensor.metrics.probeTitle.lower().startswith('tamper')
        sensor.is_alarm = sensor.devtype.lower().startswith('sensor')

    # Try to attach Battery sensors to their root Device
    for sensor in sensors:
        if sensor.devtype.lower() == 'battery':
            tree[sensor.devid]['has_battery'] = int(sensor.metrics.level)
            sensor.is_battery = True

    # Determine if a device has hidden sensor
    for sensor in sensors:
        if sensor.hidden:
            tree[sensor.devid]['has_hidden'] = True

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
        sensor = checkSensorOwner(request.user.username, key, zid, devid, instid, sid)
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


# Hide a sensor device
@login_required
def hideDeviceAction(request, key, zid, devid):

    # TODO: write a new decorator
    if not checkSensorOwner(request.user.username, key, zid):
        messages.error(request, _('Invalid Parameters'))
        return redirect('controllers_index')

    cmd = Command.objects.create(
        key = key,
        zid = zid,
        cmd = 'device_hide',
        parms = json.dumps({ 'devid': devid })
    )
    cmd.save()
    messages.info(request, 'Device is now hidden in this Interface')
    return HttpResponseRedirect('/frontend/sensors/' + key)


# Unhide a sensor device
@login_required
def unhideDeviceAction(request, key, zid, devid):

    # TODO: write a new decorator
    if not checkSensorOwner(request.user.username, key, zid):
        messages.error(request, _('Invalid Parameters'))
        return redirect('controllers_index')

    cmd = Command.objects.create(
        key = key,
        zid = zid,
        cmd = 'device_unhide',
        parms = json.dumps({ 'devid': devid })
    )
    cmd.save()
    messages.info(request, 'Device is now visible in this Interface')
    return HttpResponseRedirect('/frontend/sensors/' + key)


# Hide a sensor
@login_required
def hideSensorAction(request, key, zid, devid, instid, sid):

    sensor = checkSensorOwner(request.user.username, key, zid, devid, instid, sid)
    if not sensor:
        messages.error(request, _('Invalid Parameters'))
        return redirect('controllers_index')

    cmd = Command.objects.create(
        key = key,
        zid = zid,
        cmd = 'sensor_hide',
        parms = json.dumps({ 'devid': devid, 'instid': instid, 'sid': sid })
    )
    cmd.save()

    logger.debug(sensor)
    sensor.hidden = True
    sensor.save()
    logger.debug(sensor)

    messages.info(request, 'Sensor is now hidden in this Interface')
    return HttpResponseRedirect('/frontend/sensors/' + key)


# Unhide a sensor
@login_required
def unhideSensorAction(request, key, zid, devid, instid, sid):

    sensor = checkSensorOwner(request.user.username, key, zid, devid, instid, sid)
    if not sensor:
        messages.error(request, _('Invalid Parameters'))
        return redirect('controllers_index')

    cmd = Command.objects.create(
        key = key,
        zid = zid,
        cmd = 'sensor_unhide',
        parms = json.dumps({ 'devid': devid, 'instid': instid, 'sid': sid })
    )
    cmd.save()

    sensor.hidden = False
    sensor.save()

    messages.info(request, 'Sensor is now visible in this Interface')
    return HttpResponseRedirect('/frontend/sensors/' + key)


# Unhide all sensor for a device
@login_required
def unhideAllSensorAction(request, key, zid, devid):

    if not checkSensorOwner(request.user.username, key, zid):
        messages.error(request, _('Invalid Parameters'))
        return redirect('controllers_index')

    cmd = Command.objects.create(
        key = key,
        zid = zid,
        cmd = 'sensor_all_unhide',
        parms = json.dumps({ 'devid': devid })
    )
    cmd.save()

    Sensor.objects.filter(key=key, zid=zid, devid=devid).update(hidden=False)

    messages.info(request, 'All hidden Sensors are now visible in this Interface')
    return HttpResponseRedirect('/frontend/sensors/' + key)
