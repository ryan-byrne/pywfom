from mongoengine import *

# ********** Arduino *************

class Pin(EmbeddedDocument):
    name = StringField()
    pin = IntField()

class Arduino(EmbeddedDocument):
    port = StringField()
    trigger = IntField()
    leds = EmbeddedDocumentListField(Pin)
    daq = EmbeddedDocumentListField(Pin)

# ********** Camera *************

class Aoi(EmbeddedDocument):
    binning = StringField()
    x = IntField()
    y = IntField()
    height = IntField()
    width = IntField()
    centered = BooleanField()

class Camera(EmbeddedDocument):
    interface = StringField()
    index = IntField()
    id = StringField()
    aoi = EmbeddedDocumentField(Aoi)
    primary = BooleanField()

# ********** File *************

class File(EmbeddedDocument):
    run_length = FloatField()
    run_length_unit = StringField()
    number_of_runs = IntField()
    directory = StringField()

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

class Mouse(Document):
    name = StringField(required=True)

# Frame
class Frame(Document):
    image = ImageField()
    index = IntField()
    data = StringField()

class Run(Document):
    frames = ListField(ReferenceField(Frame))
    user = ReferenceField(User)
    mouse = ReferenceField(Mouse)
    configuration = ReferenceField(Configuration)
