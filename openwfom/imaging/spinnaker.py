import numpy as np
import threading, time, traceback, cv2

try:
    import PySpin
except ModuleNotFoundError:
    print("\nPySpin is not installed")
    print("\nFollow the directions here to install it:")
    print("\nhttps://github.com/ryan-byrne/openwfom/wiki/Camera-Setup/#installing-the-spinnaker-sdk\n")
    raise

class FlirError(Exception):
    pass

class Camera(object):
    """docstring for Flir."""

    def __init__(self, index=0, name=""):

        self.settings = {}

        self.settings['index'] = index
        self.settings['name'] = name
        self.settings["type"] = "spinnaker"
        self.types = {
            "AcquisitionFrameRate":float,
            "index":int,
            "name":str,
            "Height":int,
            "Width":int,
            "OffsetX":int,
            "OffsetY":int,
            "TriggerSource":str,
            "AcquisitionMode":str,
            "TriggerMode":str
        }
        self.pointers = {
            float:PySpin.CFloatPtr,
            int:PySpin.CIntegerPtr,
            str:PySpin.CEnumerationPtr
        }

        self.active, self.paused = False, True

        self.system = PySpin.System.GetInstance()
        self.error_msg = ""

        # Check chosen index for a camera
        try:
            print("{0} : Connecting to Camera (PySpin Index: {1})".format(self.settings["name"], self.settings["index"]))
            self.camera = self.system.GetCameras()[self.settings['index']]
            print("{0} : Initialising (FLIR SN: {1})".format(self.settings["name"], self.get_serial_number()))
            # initialize camera and create node map
            try:
                self.camera.DeInit()
                self.camera.Init()
                self.active = True
            except PySpin.SpinnakerException:
                self.error_msg = "Camera is already started at idx={0}".format(self.settings["index"])
                self._error_frame()
            self.nodemap = self.camera.GetNodeMap()
        except IndexError:
            self.error_msg = "No FLIR Camera Found (idx={0})".format(self.settings["index"])
            print("ERROR: "+self.error_msg)
            self._error_frame()
            return

        # Get the current setting of the camera
        self.get(list(self.types.keys()))

        # Create a temporary frame while the camera loads
        self.frame = np.zeros((500,500), 'uint8')

        threading.Thread(target=self._update_frames).start()

    def set(self, param, value=""):

        self._stop_camera()

        if type(param).__name__ == 'dict':
            for p in param.keys():
                self._set(p, param[p])
        else:
            self._set(param, value)

        self._start_camera()
        self.paused = False

    def _set(self, param, value):

        if not self.paused:
            print("{0} : Unable to change settings. Camera is still acquiring.".format(self.settings["name"]))
            return
        elif param in ['name', 'index', 'type']:
            return

        node = self.pointers[self.types[param]](self.nodemap.GetNode(param))

        if self.types[param] == str:
            node.SetIntValue(node.GetEntryByName(value).GetValue())
            return
        elif self.types[param] == float:
            pass
        else:
            if param in ["Height", "Width"]:
                min = 40
            else:
                min = self.get_min(param)
            max = self.get_max(param)
            inc = self.get_inc(param)

            if value > max:
                value = max
            elif value < min:
                value = min
            else:
                pass

            while not (value - min)%inc == 0:
                value += 1

        node.SetValue(value)

    def get(self, param=None):

        self._stop_camera()

        if type(param).__name__ == "list":
            for p in param:
                self._get(p)
        else:
            self._get(param)

        self._start_camera()

    def _get(self, param):

        if param in ["index", "name", "type"]:
            return param

        print("{0} : Getting {1} -> ".format(self.settings['name'], param), end="")

        node = self.pointers[self.types[param]](self.nodemap.GetNode(param))

        if self.types[param] == str:
            value = node.GetCurrentEntry().GetSymbolic()
        else:
            value = node.GetValue()

        print(value)
        self.settings[param] = value
        return value

    def get_max(self, param):
        node = self.pointers[self.types[param]](self.nodemap.GetNode(param))
        return node.GetMax()

    def get_inc(self, param):
        node = self.pointers[self.types[param]](self.nodemap.GetNode(param))
        return node.GetInc()

    def get_min(self, param):
        node = self.pointers[self.types[param]](self.nodemap.GetNode(param))
        return node.GetMin()

    def get_serial_number(self):
        return PySpin.CStringPtr(self.camera.GetTLDeviceNodeMap().GetNode('DeviceSerialNumber')).GetValue()

    def _update_frames(self):

        self.active = True

        while self.active:
            if self.paused:
                continue
            try:
                image_result = self.camera.GetNextImage(1000)
                img = np.reshape(   image_result.GetData(),
                                    (image_result.GetHeight(),image_result.GetWidth())
                                )
                image_result.Release()
                self.frame = img
                
            except PySpin.SpinnakerException as e:
                self.error_msg = "Timed out waiting for image"
                self._error_frame()
                pass

        self._stop_camera()

    def _start_camera(self):

        try:
            self.paused = False
            self.camera.BeginAcquisition()
            print("{0} : Acquiring frames".format(self.settings["name"]))
        except:
            self._error_frame()
            return

    def _stop_camera(self):
        try:
            self.paused = True
            self.camera.EndAcquisition()
            print("{0} : Stopping Acquisition".format(self.settings["name"]))
        except:
            self._error_frame()
            return

    def _error_frame(self):
        img = np.zeros((512,512,3), np.uint8)
        font                   = cv2.FONT_HERSHEY_SIMPLEX
        bottomLeftCornerOfText = (10,500)
        fontScale              = 0.75
        fontColor              = (255,255,255)
        lineType               = 2

        cv2.putText(img,"ERROR: "+self.error_msg,
            bottomLeftCornerOfText,
            font,
            fontScale,
            fontColor,
            lineType)

        self.frame = img

    def close(self):

        self.active = False

        print("Clearing Camera list...")

        self.system.GetCameras().Clear()
