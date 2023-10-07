## Cameras
# misc
from convert_ximea_camera import convert as convert_ximea_raw
from convert_boson_image import convert as convert_boson_image

# realsense
from convert_realsense_depth import convert as convert_realsense_depth
from convert_realsense_colour import convert as convert_realsense_colour

# event camera
from convert_dv_event_array import convert as convert_dv_array
from convert_dv_image import convert as convert_dv_image

from convert_radar import convert as convert_radar
from ecal.measurement.hdf5 import Meas

import os
import glob
import h5py

def get_channel_names(path_to_folder):
    
    measurements = Meas(path_to_folder)
    channel_names = measurements.get_channel_names()
    return channel_names

def main(): 

    print("ECAL TO HDF5 CONVERSION:")
    print()

    working_dir = os.path.dirname(__file__)
    base_dir = "ecal_data"
    measurement_name = "Exp 3"
    filename = "m2s2_cheetah_run3.hdf5"
    ecal_folder = os.path.join(working_dir,base_dir,measurement_name,"m2s2-NUC13ANKi7/")
    
    # notes source 
    print("Loading experiment notes file.")
    with open(os.path.join(working_dir,base_dir,measurement_name,"doc/description.txt"), 'r') as file:
        data = file.read()  

    print("Creating output file")
    try:
        out_file = h5py.File(os.path.join(working_dir,"output_data/%s"%(filename)),'x')
    except:
        print("An output file of that name already exists.\n")
        exit()

    commentGrp = out_file.create_group("Comments")
    setup=[data.encode("ascii")]  
    commentGrp.create_dataset("experiment_setup", shape=(len(setup),1), data=setup) 

    sensor_list = [
        "Realsense_Colour",
        "Realsense_Depth",
        "Ximea_Raw",
        "Boson_Thermal",
        "Wildtronics_Audio",
        "TI_Radar",
        "Livox_Lidar",
        "DVExplorer_Event",
                ]
    commentGrp.create_dataset("sensor_list", data=[str(sensor_list).encode("ascii")]) 


    channel_names = get_channel_names(ecal_folder)
    
    print("Available Channels: ")
    for name in channel_names:
        print("    |--",name)

    print()

    sensors_grp = out_file.create_group("Sensors")


    rs_colour_grp = sensors_grp.create_group(sensor_list[0])
    convert_realsense_colour(ecal_folder,rs_colour_grp)

    rs_depth_grp = sensors_grp.create_group(sensor_list[1])
    convert_realsense_depth(ecal_folder,rs_depth_grp)

    ximea_grp = sensors_grp.create_group(sensor_list[2])
    convert_ximea_raw(ecal_folder,ximea_grp)

    boson_grp = sensors_grp.create_group(sensor_list[3])
    convert_boson_image(ecal_folder,boson_grp)

    # convert_radar(expNum)
    # convert_boson_image(expNum)
    # convert_dv_event(expNum)

 
if __name__ == "__main__":
    main()