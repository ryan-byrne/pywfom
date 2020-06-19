from openwfom.imaging import andor, flir

def test_andor():
    zyla = andor.Camera(0)
    settings = {
        "PixelEncoding":"Mono16",
        "RollingShutterGlobalClear":True,
        "TriggerMode":"Software",
    }
    zyla.set(settings)

    for dim in [2000,1000,500,200,100]:
        for exp in [0.01, 0.001, 0.0001, 0.00001]:
            settings = {
                "AOIHeight":dim,
                "AOIWidth":dim,
                "ExposureTime":exp
            }
            zyla.set(settings)
            print("{0}x{0}, {1} exp -> {2} fps".format(dim, exp, zyla.get("FrameRate")))
    zyla.shutdown()

def test_flir():
    
