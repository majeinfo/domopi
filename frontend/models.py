from datetime import datetime
from django.db import models
from mongoengine import *


# Not sure it is useful since Users are handled in MySQL
class User(Document):
    login = StringField(max_length=64, unique=True)
    #email = StringField(max_length=128)
    password = StringField(max_length=64)
    #key = StringField(max_length=256, unique=True)          # à quoi ça sert maintenant ?
    #controllers = ListField(StringField(max_length=32))     # still usefull with the key field of Controller ?

    meta = {
        'collection': 'users',
        'indexes': [
            'login',
        ]
    }


# This is just an assocaition between a zid (Z-Wave ID) and a key
# The key is displayed on the R-Pi package - the End User associates the Controller in his Account
class Controller(Document):
    key = StringField(max_length=256)   # Controller Key
    zid = StringField(max_length=16)    # Controller ID (Z-Wave)
    description = StringField(max_length=256)   # User's defined
    login = StringField(max_length=64)

    meta = {
        'collection': 'controllers',
        'indexes': [
            'key',  # unique
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
    key = StringField(max_length=256)   # Controller Key
    zid = StringField(max_length=16)    # Controller ID (Z-Wave)
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
            ('key', 'zid', 'sid'),
        ]
    }

# Commands that must be sent back to the remote Controller
class Command(Document):
    key = StringField(max_length=256)   # user Key
    zid = StringField(max_length=16)    # Controller ID
    sid = StringField(max_length=256)   # sensor ID
    cmd = StringField(max_length=512)   # JSON command
    create_time = DateTimeField(default=datetime.now)

    meta = {
        'collection': 'commands',
        'indexes': [
            ('key', 'zid'),
        ]
    }