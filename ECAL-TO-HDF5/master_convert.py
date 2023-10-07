from convert_realsense_depth import convert as convert_realsense_depth
from convert_realsense_colour import convert as convert_realsense_colour
from convert_ximea_camera import convert as convert_ximea_raw
from convert_boson_image import convert as convert_boson_image
# from convert_dv_event import convert as convert_dv_event


from convert_radar import convert as convert_radar
from ecal.measurement.hdf5 import Meas

import os
import glob

def get_channel_names(expNum):
    base_dir = "ecal_data/Exp {0}/".format(expNum)
    working_dir = os.path.dirname(__file__)
    ecal_folder = os.path.join(working_dir,base_dir+"m2s2-NUC13ANKi7/")
    measurements = Meas(ecal_folder)
    channel_names = measurements.get_channel_names()
    return channel_names

def main(): 

    print("ECAL TO HDF5 CONVERSION:")
    print()
    # expNum = 6
    expNum = 3

    channel_names = get_channel_names(expNum)
    
    print("Available Channels: ")
    for name in channel_names:
        print("    |--",name)

    print()

    # convert_realsense_depth(expNum)
    # convert_realsense_color(expNum)
    # convert_ximea_raw(expNum)
    # convert_radar(expNum)
    # convert_boson_image(expNum)
    # convert_dv_event(expNum)

 
if __name__ == "__main__":
    main()