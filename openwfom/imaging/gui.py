import cv2
import numpy as np

# cv2 drawing variables
drawing = False
ix, iy = -1, -1

def view(winname, imgs):

    win_width = 300
    padding = 10

    frame = np.zeros((1, win_width), dtype='uint8')

    for img in imgs:
        scale = 300/img.shape[1]
        small = cv2.resize(img, (0,0), fx=scale, fy=scale)
        frame = np.concatenate(( frame, small) )

    cv2.imshow("OpenWFOM", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        return False
    else:
        return True

def draw_aoi(event, x, y, flags, param):

    global drawing, ix, iy

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x,y
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            cv2.rectangle(frame, )
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        w = x - ix
        h = y - iy
        print("{0}x{1} Rectangle, with origin at {2},{3}".format(h, w, ix, iy))
