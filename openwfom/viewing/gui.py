import cv2, time, threading, subprocess
import numpy as np
import openwfom

def _format_frame(frame, label="", to_shape=(800,800), padding=50):

    # Reformat to unsigned 8bit int if not
    if frame.dtype == 'uint16':
        frame = frame.astype('uint8')
    # Store current frame shape
    fs = frame.shape
    # Set scaling factor
    sf = min(to_shape)/(max(fs)+2*padding)
    # Resive the Frame to fit in to_shape size (w/ padding)
    frame = cv2.resize(frame, (0,0), fx=sf, fy=sf)

    # Calculate the padding in x (pad[1]) and y (pad[0])
    pad_y = int(max(0, (to_shape[0] - frame.shape[0]))/2)
    pad_x = int(max(0, (to_shape[1] - frame.shape[1]))/2)

    # Add padding
    gray = np.pad(frame, ((pad_y, pad_y), (pad_x, pad_x)), 'constant')
    # COnvert to RGB
    rgb = cv2.cvtColor(gray, cv2.COLOR_BGR2RGB)
    # Add label
    cv2.putText(rgb, label, (pad_x, pad_y+10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
    return rgb

class Frame(object):
    """docstring for Frame."""

    def __init__(self, win_name):
        # cv2 drawing variables
        self.drawing = False
        self.dragging = False
        self.ix, self.iy, self.x, self.y, self.cx, self.cy = -1,-1,-1,-1,-1,-1
        self.win_name = win_name
        self.selected_idx = 0
        self.num_sfs = 0
        self.active = True
        threading.Thread(target=self._view_frame).start()

    def _mouse_callback(self, event, x, y, flags, param):

        if event == cv2.EVENT_LBUTTONDOWN:
            if x < 800:
                # Mouse selected main frame
                self.drawing = True
                self.ix, self.iy, self.x, self.y = x,y,x,y
            else:
                # Mouse selected sub frame
                self.selected_idx = int(y/800*(self.num_sfs))

        elif event == cv2.EVENT_MOUSEMOVE:
            self.cx, self.cy = x, y
            if self.drawing:
                self.x, self.y = x, y
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
        elif event == cv2.EVENT_RBUTTONDOWN:
            self.ix, self.iy, self.x, self.y = -1, -1, -1, -1

    def view(self, img_dict):
        # Update the objects 'frame' variable
        threading.Thread(target=self._update_frame, args=(img_dict,)).start()
        return self.active

    def _view_frame(self):
        # Open a new cv2 window
        cv2.namedWindow(self.win_name)
        cv2.setMouseCallback(self.win_name, self._mouse_callback)
        # Create an empty frame
        self.frame = _format_frame(np.zeros((1000,1000), 'uint8'), 'Waiting for Images...')
        # Run a loop while the frame is active
        while self.active:
            # Draw a circle to make mouse position more visible
            cv2.circle(self.frame, (self.cx, self.cy), 10, (255,0,0), 5, 1, 0)
            # Draw a rectangle on main frame for AOI
            cv2.rectangle(self.frame,(self.ix,self.iy),(self.x,self.y),(0,255,0))
            # Show the resulting frame using OpenCV
            cv2.imshow(self.win_name, self.frame)

            # Quit the program if the Q button is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.active = False
                break

    def _update_frame(self, img_dict):
        # Calculate number of frames
        self.num_sfs = len(img_dict.keys())
        # Get name of chosen main frame
        mf_name = list(img_dict.keys())[self.selected_idx]
        # Establish the main frame
        mf = _format_frame(img_dict[mf_name], mf_name)

        # Skip calculation of there are no sub frames
        if len(img_dict.keys()) == 1:
            self.frame = mf
        else:
            sf = []
            for img_key in img_dict.keys():
                # Calculate the size of each sub frame -> MF_Height / # of Sub Frames
                sf_dim = int(mf.shape[0]/len(img_dict.keys()))
                sf.append(_format_frame(img_dict[img_key], img_key, (sf_dim, sf_dim)))

            # Combine the subframes vertically
            sf = cv2.vconcat(sf)
            # Combine subframes and main frame horizontally
            self.frame = cv2.hconcat([mf[:sf.shape[0]], sf])

    def close(self):
        self.active = False
        cv2.destroyAllWindows()

class Settings(object):
    """docstring for Settings."""

    def __init__(self, path_to_settings=""):
        self._check_java()
        self.JAR_PATH = "{0}\\viewing\\java\\JARS\\".format(openwfom.__path__[0])

    def set(self, setting):

        print("Setting {0} from the GUI...".format(setting))

        path = "{0}{1}.jar".format(self.JAR_PATH, setting)
        subprocess.call(["java", "-jar", path])

    def _check_java(self):

        print("Checking Version of Java Runtime Environment")

        try:
            out = subprocess.check_output(['java', '-version'], stderr=subprocess.STDOUT).decode("utf-8")
            version = ""
            if out[0] == "'":
                raise EnvironmentError("Java is not installed on your machine.")
            for l in out:
                if len(version) > 0 and l == '"':
                    break
                elif l in [".", "_"] or l.isdigit():
                    version += l
                else:
                    continue
            if float(version[:3]) < 1.7:
                raise EnvironmentError("Your version of Java Runtime Environment\
                is {0}. 1.7 or up is required.")

            print("JRE {0} is installed".format(version))

        except Exception as e:
            msg = "Could not find the correct version of the Java Runtime Environment"
            raise EnvironmentError(msg)
