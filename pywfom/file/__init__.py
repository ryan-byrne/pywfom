import os

class File(object):

    def __init__(self):
        self.directory = os.environ("PYWFOM_DIRECTORY")

    def set(self, **settings):
        for k,v in settings.items():
            setattr(self, k, v)

    def json(self):
        return self.__dict__
