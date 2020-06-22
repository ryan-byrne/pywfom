from openwfom.imaging import andor
import cv2, sys, h5py, time, glob, os

def test_andor():

    zyla = andor.Camera(0, True)

    for num_frms in [10, 100, 1000]:
        for comp in [0, 1, 4, 9]:
            print("{0} compression".format(comp))
            zyla.capture('frames', num_frms)
            save_hdf5(zyla, "{0}comp{1}frames".format(comp, num_frms), comp)

    #read_hdf5('frames')

    zyla.shutdown()

def save_hdf5(camera, fname, comp):
    prev_frame = camera.frame
    i = 0
    t0 = time.time()
    print(fname[5:])
    with h5py.File("data/tests/{0}.hdf5".format(fname), 'w') as h5:
        while camera.active:
            if (prev_frame==camera.frame).all():
                continue
            else:
                #print(camera.frame)
                h5.create_dataset(  "frame{0}".
                                    format(i),
                                    data=camera.frame,
                                    dtype='uint16',
                                    compression='gzip',
                                    compression_opts=comp)
                i += 1
            prev_frame = camera.frame
        print("Captured in {0} sec".format(time.time()-t0))
    h5.close()
    print("Saved in {0} sec".format(time.time()-t0))
    fsize = os.path.getsize("data/tests/{0}.hdf5".format(fname))
    print("Size: {0} GB\n".format(fsize/1000000000))

def read_hdf5(fname):
    with h5py.File("data/tests/{0}.hdf5".format(fname), 'r') as h5:
        print("Reading {0}.hdf5".format(fname))
        for name in h5.keys():
            print(h5[name])


if __name__ == '__main__':
    test_andor()
