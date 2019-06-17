import visa

class Led(object):
    """docstring for Led."""

    def __init__(self):
        pass

    def check_led():
        rm = visa.ResourceManager()
        print(rm.list_resources())
        return 1
