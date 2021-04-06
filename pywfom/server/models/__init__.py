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

# ********** File *************

class File(EmbeddedDocument):
    run_length = FloatField()
    run_length_unit = StringField()
    number_of_runs = IntField()
    directory = StringField()

# ********** Configuration *********

class Configuration(Document):
    name = StringField()
    arduino = EmbeddedDocumentField(Arduino)
    cameras = EmbeddedDocumentListField(Camera)
    file = EmbeddedDocumentField(File)

class User(Document):
    name = StringField()
    email = EmailField()
    default = ReferenceField(Configuration)
    configurations = ListField(ReferenceField(Configuration))
