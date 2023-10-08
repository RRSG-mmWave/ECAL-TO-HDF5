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

## other sensors
from convert_radar import convert as convert_radar
from convert_wildtronics_audio import convert as convert_wildtronics_audio
from convert_livox_point_cloud import convert as convert_livox_point_cloud


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
    ecal_folder = os.path.join(working_dir,base_dir,measurement_name,"m2s2-NUC13ANKi7/")
    
    # notes source 
    print("Loading experiment notes file.")
    with open(os.path.join(working_dir,base_dir,measurement_name,"doc/description.txt"), 'r') as file:
        data = file.read()  

    print("Creating output file")
    filename = "m2s2_cheetah_run3.hdf5"
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

    # unpack realsense colour
    rs_colour_grp = sensors_grp.create_group(sensor_list[0])
    convert_realsense_colour(ecal_folder,rs_colour_grp)

    # unpack realsense depth
    rs_depth_grp = sensors_grp.create_group(sensor_list[1])
    convert_realsense_depth(ecal_folder,rs_depth_grp)

    # unpack ximea raw image
    ximea_grp = sensors_grp.create_group(sensor_list[2])
    convert_ximea_raw(ecal_folder,ximea_grp)

    # unpack boson thermal image
    boson_grp = sensors_grp.create_group(sensor_list[3])
    convert_boson_image(ecal_folder,boson_grp)

    # unpack audio
    audio_grp = sensors_grp.create_group(sensor_list[4])
    convert_wildtronics_audio(ecal_folder,audio_grp)

    # unpack radar data
    path_to_config = os.path.join(working_dir,"other_data","config.json")
    radar_grp = sensors_grp.create_group(sensor_list[5])
    convert_radar(ecal_folder,path_to_config,radar_grp)

    # unpack lidar PCDs
    lidar_grp = sensors_grp.create_group(sensor_list[6])
    convert_livox_point_cloud(ecal_folder,lidar_grp)

    # unpack event camera arrays
    event_grp = sensors_grp.create_group(sensor_list[7])
    event_array_grp = event_grp.create_group("Event_Arrays")
    convert_dv_array(ecal_folder,event_array_grp)

    # unpack event camera images
    event_image_grp = event_grp.create_group("Event_Images")
    convert_dv_image(ecal_folder,event_image_grp)
    exit()
    
 
if __name__ == "__main__":
    main()