from mongoengine import *

# ********** Arduino *************

class Pin(EmbeddedDocument):
    name = StringField()
    pin = IntField()

class Stim(EmbeddedDocument):
    pins = EmbeddedDocumentListField(Pin)

class Arduino(EmbeddedDocument):
    port = StringField()
    trigger = IntField()
    leds = EmbeddedDocumentListField(Pin)
    daq = EmbeddedDocumentListField(Pin)
    stim = EmbeddedDocumentListField(Stim)

# ********** Camera *************

class Aoi(EmbeddedDocument):
    binning = StringField(choices=['1x1','2x2','4x4','8x8'], max_length=3)
    x = IntField()
    y = IntField()
    height = IntField(required=True)
    width = IntField(required=True)
    centered = BooleanField()

class Camera(EmbeddedDocument):
    interface = StringField(required=True, choices=['opencv','spinnaker','andor','test'])
    index = IntField(required=True)
    id = StringField()
    aoi = EmbeddedDocumentField(Aoi)
    primary = BooleanField()

# ********** File *************

class File(EmbeddedDocument):
    run_length = FloatField()
    run_length_unit = StringField()
    number_of_runs = IntField()

# ********** Configuration *********

class Configuration(Document):
    name = StringField(unique=True)
    arduino = EmbeddedDocumentField(Arduino)
    cameras = EmbeddedDocumentListField(Camera)
    file = EmbeddedDocumentField(File)

# User

class User(Document):
    username = StringField(unique=True, required=True)
    email = EmailField()
    password = StringField(required=True)
    default = ReferenceField(Configuration)
    configurations = ListField(ReferenceField(Configuration))

class Frame(Document):
    timestamp = DateTimeField(required=True)
    daq = ListField(IntField)
    leds = ListField(BooleanField)
    stim = ListField(IntField)
    images = StringField(required=True)

class Mouse(Document):
    name = StringField(required=True, unique=True)

class Run(Document):
    config = ReferenceField(Configuration)
    mouse = ReferenceField(Mouse)
    user = ReferenceField(User)
    frames = ListField(ReferenceField(Frame))
