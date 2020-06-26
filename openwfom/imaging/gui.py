import cv2, time
import numpy as np

def _format_frame(frame, to_shape=(800,800), padding=50):

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

    # Add padding adn return
    return np.pad(frame, ((pad_y, pad_y), (pad_x, pad_x)), 'constant')

class Frame(object):
    """docstring for Frame."""

    def __init__(self, win_name):
        # cv2 drawing variables
        self.drawing = False
        self.ix, self.iy = -1, -1
        self.win_name = win_name
        cv2.namedWindow(self.win_name)
        cv2.setMouseCallback(self.win_name, self._draw_aoi)

    def _draw_aoi(self, event, x, y, flags, param):

        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.ix, self.iy = x,y
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                cv2.rectangle(self.frame,(self.ix,self.iy),(x,y),(0,255,0),-1)
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            cv2.rectangle(self.frame,(self.ix,self.iy),(x,y),(0,255,0),-1)

    def view(self, main_frame, sub_frames=None):

        mf = _format_frame(main_frame)

        # Skip calculation of there are no sub frames
        if not sub_frames:
            self.frame = mf
        else:
            sf = []
            for sub_frame in sub_frames:
                # Calculate the size of each sub frame -> MF_Height / # of Sub Frames
                sf_dim = int(mf.shape[0]/len(sub_frames))
                sf.append(_format_frame(sub_frame, (sf_dim, sf_dim)))

            # Combine the subframes vertically
            sf = cv2.vconcat(sf)
            # Combine subframes and main frame horizontally
            self.frame = cv2.hconcat([mf[:sf.shape[0]], sf])

        # Show the resulting frame using OpenCV
        cv2.imshow(self.win_name, self.frame)

        # Quit the program if the Q button is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            return False
        else:
            return True

    def close(self):
        cv2.destroyAllWindows()
