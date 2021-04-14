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
    fullHeight = IntField()
    fullWidth = IntField()
    centered = BooleanField()

class Camera(EmbeddedDocument):
    interface = StringField(required=True, choices=['opencv','spinnaker','andor','test'])
    index = IntField(required=True)
    dtype = StringField(choices=['uint8','uint16','uint32'])
    id = StringField()
    aoi = EmbeddedDocumentField(Aoi)
    framerate = FloatField()
    primary = BooleanField()

# ********** File *************

class File(EmbeddedDocument):
    run_length = FloatField()
    run_length_unit = StringField()
    number_of_runs = IntField()
    size = IntField()

# ********** Configuration *********

class Configuration(Document):
    name = StringField(unique=True, required=True)
    arduino = EmbeddedDocumentField(Arduino, required=True)
    cameras = EmbeddedDocumentListField(Camera, required=True)
    file = EmbeddedDocumentField(File, required=True)

# User

class User(Document):
    username = StringField(unique=True, required=True)
    email = EmailField()
    password = StringField(required=True)
    default = ReferenceField(Configuration)
    configurations = ListField(ReferenceField(Configuration))

class Frame(Document):
    daq = ListField(IntField)
    leds = ListField(BooleanField)
    stim = ListField(IntField)
    file = StringField(required=True)

class Mouse(Document):
    name = StringField(required=True, unique=True)

class Run(Document):
    timestamp = DateTimeField()
    configuration = ReferenceField(Configuration)
    mouse = ReferenceField(Mouse)
    user = ReferenceField(User)
    frames = ListField(ReferenceField(Frame))
