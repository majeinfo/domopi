from datetime import datetime
#from django.db import models
from mongoengine import *


# Not sure it is useful since Users are handled in MySQL
class User(Document):
    login = StringField(max_length=64, unique=True)
    password = StringField(max_length=64)
    #key = StringField(max_length=256, unique=True, required=False)          # still useful ?
    #controllers = ListField(StringField(max_length=32), required=False)     # still usefull with the key field of Controller ?
    email = StringField(max_length=64, required=False)
    timezone = StringField(max_length=32, required=False, default='UTC')
    address = StringField(max_length=128, required=False)
    phonenu = StringField(max_length=16, required=False)
    lat = FloatField(required=False)
    lng = FloatField(required=False)
    # TODO: info about subscription

    meta = {
        'collection': 'users',
        'indexes': [
            'login',
        ]
    }


# This is just an association between a zid (Z-Wave ID) and a key
# The key is displayed on the R-Pi package - the End User associates the Controller in his Account
class Controller(Document):
    key = StringField(max_length=256)   # Controller Key
    zid = StringField(max_length=16)    # Controller ID (Z-Wave)
    localip = StringField(max_length=16, required=False)
    description = StringField(max_length=256, required=False)   # User's defined
    login = StringField(max_length=64, required=False)
    doversion = StringField(max_length=8, required=False)
    timezone = StringField(max_length=32, required=False)

    meta = {
        'collection': 'controllers',
        'indexes': [
            'key',  # unique
        ]
    }


# Log from Controller
class Log(Document):
    key = StringField(max_length=256)   # Controller Key
    date = DateTimeField()
    level = StringField(max_length=8)
    msg = StringField()

    meta = {
        'collection': 'logs',
        'indexes': [
            ('key', 'date')
        ]
    }


class Metrics(EmbeddedDocument):
    title = StringField(max_length=64)
    probeTitle = StringField(max_length=64)
    scaleTitle = StringField(max_length=32)
    is_level_number = BooleanField()
    level = FloatField()
    on_off = BooleanField()
    change = StringField(max_length=32)


# Sensor Description and Status - updated by the remote Controller
class Sensor(Document):
    TYPE_SWITCH = 'switchBinary'
    TYPE_BATTERY = 'battery'
    TYPE_SENSOR_BINARY = 'sensorBinary'
    TYPE_SENSOR_MULTILEVEL = 'sensorMultilevel'

    key = StringField(max_length=256)   # Controller Key
    zid = StringField(max_length=16)    # Controller ID (Z-Wave)
    devid = StringField(max_length=16)
    instid = StringField(max_length=16)
    sid = StringField(max_length=256)   # sensor ID
    description = StringField(max_length=256)
    devtype = StringField(max_length=64)
    tags = ListField(StringField(max_length=64))
    metrics = EmbeddedDocumentField(Metrics)
    last_update = DateTimeField()
    #icon

    meta = {
        'collection': 'sensors',
        'indexes': [
            ('key', 'zid'),
        ]
    }

    def getInternalName(self):
        return self.devid + '-' + self.instid + '-' + self.sid

    @staticmethod
    def buildInternalName(devid, instid, sid):
        return devid + '-' + instid + '-' + sid

    @staticmethod
    def splitInternalName(iname):
        parts = iname.split('-')
        return parts[0], parts[1], '-'.join(parts[2:])


# Commands that must be sent back to the remote Controller
class Command(Document):
    key = StringField(max_length=256)   # user Key
    zid = StringField(max_length=16)    # Controller ID
    cmd = StringField(max_length=512)
    parms = StringField(max_length=1024*32) # JSON value
    create_time = DateTimeField(default=datetime.now)

    meta = {
        'collection': 'commands',
        'indexes': [
            ('key', 'zid'),
        ]
    }


# Rules definition
class RuleCondition(EmbeddedDocument):
    THRESHOLD = 'thresholdcond'
    TIME = 'timecond'
    STATUS = 'statuscond'
    STATUS_ON = 'ON'
    STATUS_OFF = 'OFF'
    condtype = StringField(max_length=32)
    devid = StringField(max_length=16, required=False)
    instid = StringField(max_length=16, required=False)
    sid = StringField(max_length=256, required=False)
    value = StringField(max_length=256, required=False)
    testtype = StringField(max_length=4, required=False)
    starttime = StringField(max_length=16, required=False)
    endtime = StringField(max_length=16, required=False)
    days = StringField(max_length=8, required=False)

class RuleAction(EmbeddedDocument):
    SENSORCMD = 'sensorcmd'
    EMAILCMD = 'emailcmd'
    CMD_ON = 'ON'
    CMD_OFF = 'OFF'
    actiontype = StringField(max_length=32)
    devid = StringField(max_length=16, required=False)
    instid = StringField(max_length=16, required=False)
    sid = StringField(max_length=256, required=False)
    value = StringField(max_length=256, required=False)
    email = StringField(max_length=64, required=False)
    subject = StringField(max_length=256, required=False)
    content = StringField(max_length=256, required=False)

class Rule(Document):
    key = StringField(max_length=256)   # user Key
    zid = StringField(max_length=16)    # Controller ID
    description = StringField(max_length=256)
    conditions = EmbeddedDocumentListField(RuleCondition, required=False)
    actions = EmbeddedDocumentListField(RuleAction, required=False)

    meta = {
        'collection': 'rules',
        'indexes': [
            ('key', 'zid'),
        ]
    }


# Utilities functions:
# Check the User towards the key
def checkControllerOwner(username, key):
    try:
        controller = Controller.objects.get(login=username, key=key)
    except:
        return None

    return controller


# Check the User towards the key/zid/sid
def checkSensorOwner(username, key, zid, devid=None, instid=None, sid=None):
    try:
        controller = Controller.objects.get(login=username, key=key, zid=zid)
    except:
        return None

    if not devid or not instid or not sid: return controller

    try:
        sensor = Sensor.objects.get(key=key, devid=devid, instid=instid, sid=sid)
    except:
        return None

    return sensor
