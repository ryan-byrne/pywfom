import numpy as np
import threading, time, traceback, os, ctypes, platform, queue
import sys
from PIL import Image, ImageDraw, ImageFont

def error_frame(msg):

    # Create a frame announcing the error
    img = Image.fromarray(np.zeros((500,500), "uint8"))
    draw = ImageDraw.Draw(img)
    draw.text((10, 175), "ERROR:", 255)
    draw.text((10,225), msg, 255)
    return np.asarray(img)

def loading_frame():
    # Create a frame announcing the error
    img = Image.fromarray(np.zeros((500,500), "uint8"))
    draw = ImageDraw.Draw(img)
    draw.text((200,250), "Loading Frame...", 255)
    return np.asarray(img)

def update_frame(camera):

    camera.active = True

    while camera.active:
        try:
            camera.frame = camera.read()
            camera.AcquisitionFrameRate = camera.get("AcquisitionFrameRate")
        except Exception as e:
            camera.frame = error_frame(str(e))

class Test(object):

    def __init__(self, settings):

        self.default = {
            "device":"test",
            "name":"default1",
            "index":0,
            "Height":700,
            "Width":1200,
            "AcquisitionFrameRate":50.0,
            "master":True,
            "dtype":"uint8",
            "OffsetX":0,
            "OffsetY":0
        }

        self.set(settings)

        threading.Thread(target=update_frame, args=(self,)).start()

    def start(self):
        pass

    def stop(self):
        pass

    def read(self):
        if self.dtype == 'uint8':
            max = 255
        else:
            max = 65024

        if self.master:
            time.sleep(1/self.AcquisitionFrameRate)

        return np.random.randint(0,max,size=(self.Height, self.Width), dtype=self.dtype)

    def set(self, setting, value=None):

        self.stop()

        self.frame = loading_frame()

        if type(setting).__name__ == 'dict':
            for k, v in setting.items():
                setattr(self, k, v)
        else:
            setattr(self, setting, value)

        self.start()

    def get(self, setting):
        return getattr(self, setting)

    def get_max(self, setting):
        maximums = {
            "Height":1000,
            "Width":1400,
            "AcquisitionFrameRate":100
        }
        return maximums[setting]

    def close(self):
        self.active = False

class Spinnaker(object):

    def __init__(self, settings):

        try:
            print("Importing Spinnaker SDK Libraries...")
            import PySpin

            self.writable, self.available = PySpin.IsWritable, PySpin.IsAvailable

            self._pointers = {
                PySpin.intfIFloat: PySpin.CFloatPtr,
                PySpin.intfIBoolean: PySpin.CBooleanPtr,
                PySpin.intfIInteger: PySpin.CIntegerPtr,
                PySpin.intfIEnumeration: PySpin.CEnumerationPtr,
                PySpin.intfIString: PySpin.CStringPtr
            }

            self.settings = {}
            self.methods = {}

            self.system = PySpin.System.GetInstance()
            self.camera = self.system.GetCameras().GetByIndex(settings['index'])
        except Exception as e:
            for k, v in settings.items():
                setattr(self, k, v)
            if type(e).__name__ == "ModuleNotFoundError":
                msg = "\nYou have not installed PySpin\n\n\
                Follow the instructions at:\n\nhttps://github.com/ryan-byrne/pywfom/wiki/Cameras:-Spinnaker\n\n"
            else:
                msg = str(e)
            self.frame = error_frame("({0}) {1}".format(self.name, msg))
            print(msg)
            return
        self.camera.Init()

        for node in self.camera.GetNodeMap().GetNodes():
            pit = node.GetPrincipalInterfaceType()
            name = node.GetName()
            if pit == PySpin.intfICommand:
                self.methods[name] = PySpin.CCommandPtr(node)
            elif pit in self._pointers:
                self.settings[name] = self._pointers[pit](node)


        self.set("AcquisitionFrameRateEnable", True)

        self.set(settings)

        threading.Thread(target=update_frame, args=(self,)).start()

    def start(self):
        self.camera.BeginAcquisition()

    def stop(self):
        try:
            self.camera.EndAcquisition()
        except:
            pass

    def read(self):
        return self.camera.GetNextImage(1000).GetNDArray()

    def set(self, setting, value=None):

        self.stop()
        self.frame = loading_frame()
        if type(setting).__name__ == 'dict':
            for k, v in setting.items():
                self._set(k, v)
        else:
            self._set(setting, value)

        self.start()

    def _set(self, setting, value):

        if setting in ['name', 'device']:
            pass
        elif setting == 'index':
            # TODO: Change Index
            pass
        elif setting == 'master':
            # TODO: Change Trigger Mode
            pass
        elif setting == 'dtype':
            # TODO: Change Format
            pass
        else:

            node = self.settings[setting]

            if node.GetName() == "AcquisitionFrameRateEnable":
                node.SetValue(value)
                return

            if value > self.get_max(setting):
                value = self.get_max(setting)
                print("({0}) Setting {1} to the maximum value of {2}".format(self.name, setting, value))
            elif value < self.get_min(setting):
                value = self.get_min(setting)
                print("({0}) Setting {1} to the minimum value of {2}".format(self.name, setting, value))

            if node.GetName() == "AcquisitionFrameRate":
                node.SetValue(value)
                setattr(self, setting, value)
                return

            while value%self.get_inc(setting) != 0:
                value+= 1

            node.SetValue(value)

        setattr(self, setting, value)

    def get(self, setting):
        try:
            return self.settings[setting].GetValue()
        except:
            try:
                return self.settings[setting].ToString()
            except:
                return None

    def get_max(self, setting):
        return self.settings[setting].GetMax()

    def get_min(self, setting):
        return self.settings[setting].GetMin()

    def get_inc(self, setting):
        return self.settings[setting].GetInc()

    def close(self):
        self.active = False

class Andor(object):

    def __init__(self, settings):

        try:
            print("Importing Andor SDK3 Libraries...")
            global andor
            from pywfom.utils import andor
            print("Initializing Andor Camera at index "+settings['index'])
            self.camera = andor.Open(settings['index'])
            if self.get("SerialNumber")[:3] == "SFT":
                raise andor.AndorError
        except Exception as e:
            for k, v in settings.items():
                setattr(self, k, v)
            self.frame = error_frame("({0}) {1}".format(self.name, str(e)))
            return

        self.buffers = queue.Queue()
        self.set(settings)

        threading.Thread(target=update_frame, args=(self,)).start()

    def start(self):

        # Create new buffers
        for i in range(10):
            buf = np.zeros((self.get("ImageSizeBytes")), 'uint8')
            andor.QueueBuffer(
                self.camera,
                buf.ctypes.data_as(andor.POINTER(andor.AT_U8)),
                buf.nbytes
            )
            self.buffers.put(buf)

        # Start the acquisition
        andor.Command(self.camera, "AcquisitionStart")

    def stop(self):
        try:
            # CLear all buffers and queues
            andor.Command(self.camera, "AcquisitionStop")
            self.buffers.queue.clear()
            andor.Flush(self.camera)
        except:
            pass

    def read(self):

        buf = self.buffers.get()
        andor.WaitBuffer(self.camera, 1000)
        img = (buf[::2]*buf[1::2]).reshape(self.Height, self.Width)
        andor.QueueBuffer(
            self.camera,
            buf.ctypes.data_as(andor.POINTER(andor.AT_U8)),
            buf.nbytes
        )
        self.buffers.put(buf)
        return img

    def set(self, setting, value=None):

        self.stop()
        self.frame = loading_frame()
        if type(setting).__name__ == 'dict':
            for k, v in setting.items():
                self._set(k, v)
        else:
            self._set(setting, value)
        self.start()

    def _set(self, setting, value):

        settings = {
            "Height":"AOIHeight",
            "Width":"AOIWidth",
            "OffsetX":"AOILeft",
            "OffsetY":"AOITop",
            "AcquisitionFrameRate":"FrameRate"
        }

        if setting in ['name', 'device']:
            pass
        elif setting == 'index':
            # TODO: Change Index
            pass
        elif setting == 'master':
            # TODO: Change Trigger Mode
            pass
        elif setting == 'dtype':
            idx = {"uint16":"Mono16",'uint8':"Mono12",'uint32':"Mono32"}
            andor.SetEnumString(self.camera, "PixelEncoding", idx[value])
        else:
            try:
                andor.SetEnumString(self.camera, settings[setting], value)
            except:
                try:
                    andor.SetBool(self.camera, settings[setting], value)
                except:
                    if value > self.get_max(settings[setting]):
                        value = self.get_max(settings[setting])
                    elif value < self.get_min(settings[setting]):
                        value = self.get_min(settings[setting])
                    try:
                        andor.SetInt(self.camera, settings[setting], value)
                    except:
                        andor.SetFloat(self.camera, settings[setting], value)

        setattr(self, setting, value)

    def get(self, setting):

        settings = {
            "Height":"AOIHeight",
            "Width":"AOIWidth",
            "OffsetX":"AOILeft",
            "OffsetY":"AOITop",
            "AcquisitionFrameRate":"FrameRate"
        }

        try:
            value = andor.GetInt(self.camera, setting).value
        except:
            try:
                value = andor.GetFloat(self.camera, setting).value
            except:
                try:
                    value = andor.GetString(self.camera, setting, 255).value
                except:
                    idx = andor.GetEnumIndex(self.camera, setting).value
                    value = andor.GetEnumStringByIndex(self.camera, setting, idx, 255).value
        return value

    def get_max(self, setting):
        try:
            return andor.GetIntMax(self.camera, setting).value
        except:
            return andor.GetFloatMax(self.camera, setting).value

    def get_min(self, setting):
        try:
            return andor.GetIntMin(self.camera, setting).value
        except:
            return andor.GetFloatMin(self.camera, setting).value

    def get_inc(self, setting):
        return self.settings[setting].GetInc()

    def close(self):
        self.active = False

class Webcam(object):

    def __init__(self, settings):

        print("Importing Webcam Libraries...")
        global cv2
        import cv2

        self.default = {
            "device":"test",
            "name":"default1",
            "index":0,
            "Height":700,
            "Width":1200,
            "AcquisitionFrameRate":50.0,
            "master":True,
            "dtype":"uint8",
            "OffsetX":0,
            "OffsetY":0
        }

        self.set(settings)

        if not self.camera.isOpened():
            self.frame = error_frame("({0}) no Webcam found at index:{1}".format(self.name, self.index))
            return

        threading.Thread(target=update_frame, args=(self,)).start()

    def start(self):
        pass

    def stop(self):
        pass

    def read(self):
        ret, img = self.camera.read()
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        x, y, w, h = self.OffsetX, self.OffsetY, self.Width, self.Height
        return img_gray[y:h+y, x:w+x]

    def set(self, setting, value=None):

        print("Adjusting webcam settings...")

        self.stop()

        self.frame = loading_frame()

        if type(setting).__name__ == 'dict':
            for k, v in setting.items():
                self._set(k, v)
        else:
            self._set(setting, value)

        self.start()

    def _set(self, setting, value):

        if setting == "index":
            self.camera = cv2.VideoCapture(value)
        else:
            pass

        setattr(self, setting, value)

    def get(self, setting):

        prop_ids = {
            "AcquisitionFrameRate":cv2.CAP_PROP_FPS,
            "Height":cv2.CAP_PROP_FRAME_HEIGHT,
            "Width":cv2.CAP_PROP_FRAME_WIDTH
        }

        if setting in prop_ids.keys():
            return self.camera.get(prop_ids[setting])
        else:
            return getattr(self, setting)

    def get_max(self, setting):

        maximums = {
            "Height":int(self.camera.get(4)),
            "Width":int(self.camera.get(3))
        }
        return maximums[setting]

    def close(self):
        self.active = False

DEVICES = {
    'andor':Andor,
    'webcam':Webcam,
    'test':Test,
    'spinnaker':Spinnaker
}
