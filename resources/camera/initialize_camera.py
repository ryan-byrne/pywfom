
import time

def initialise_camera(settings) :

    print("Intialising Andor SDK3")
    sdk3 = ATCore() # Initialise SDK3
    deviceCount = sdk3.get_int(sdk3.AT_HNDL_SYSTEM,"DeviceCount");

    print("Found : ",deviceCount," device(s)");

    if deviceCount > 0 :

        try :
            print(" Opening camera ");
            hndl = sdk3.open(0);

            print(" Deploying Camera Settings")
            initialization_settings = [
                ["PixelEncoding", "Mono16"],
                ["TriggerMode", "Software"],
                ["CycleMode", "Continuous"],
                ["AOIBinning", settings["binning"]]
                ["PixelReadoutRate", "100 MHz"],
                ["ExposureTime", float(settings["framerate"])]
            ]
            for setting in initialization_settings:
                print("  Setting {0}".format(setting[0]))
                if type(setting[1]) == str:
                    sdk3.set_enum_string(hndl, setting[0], setting[1])
                    actual = setting[1]
                else:
                    sdk3.set_float(hndl, setting[0], setting[1])
                    actual = sdk3.get_float(hndl, setting[0])
                print("   {0} set to: {1}".format(setting[0], actual))
            return sdk3, hndl

        except ATCoreException as err :
          print("     SDK3 Error {0}".format(err));
        print("  Closing camera");
        sdk3.close(hndl);
    else :
        print("Could not connect to camera");
