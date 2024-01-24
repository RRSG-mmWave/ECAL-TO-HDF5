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

    # Specify data path and output names
    base_dir = "ecal_data"
    measurement_name = "Exp 3"
    host_username = "m2s2-NUC13ANKi7/" # it found as a sub dir of ecal meas folder 
    filename = "m2s2_cheetah_run3.hdf5"
    
    # use this map to enable sensors 
    sensor_list = {
        "Realsense_Colour"  :   False,
        "Realsense_Depth"   :   False,
        "Ximea_Raw"         :   False,
        "Boson_Thermal"     :   False,
        "Wildtronics_Audio" :   False,
        "TI_Radar"          :   True,
        "Livox_Lidar"       :   False,
        "DVExplorer_Event"  :   False
    }

    # Only thing that might need to be changed after this point is channel name used 
    # which is an argument to each convert function. Check default against channels 
    # listed in terminal when this script is run 
    
    working_dir = os.path.dirname(__file__)
    ecal_folder = os.path.join(working_dir,base_dir,measurement_name,host_username)
    
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


    commentGrp.create_dataset("sensor_list", data=[str(sensor_list).encode("ascii")]) 


    channel_names = get_channel_names(ecal_folder)
    
    print("Available Channels: ")
    for name in channel_names:
        print("    |--",name)

    print()

    sensors_grp = out_file.create_group("Sensors")

    # unpack realsense colour
    if sensor_list["Realsense_Colour"]:
        rs_colour_grp = sensors_grp.create_group(sensor_list[0])
        convert_realsense_colour(ecal_folder,rs_colour_grp)

    # unpack realsense depth
    if sensor_list["Realsense_Depth"]:
        rs_depth_grp = sensors_grp.create_group(sensor_list[1])
        convert_realsense_depth(ecal_folder,rs_depth_grp)

    # unpack ximea raw image
    if sensor_list["Ximea_Raw"]:
        ximea_grp = sensors_grp.create_group(sensor_list[2])
        convert_ximea_raw(ecal_folder,ximea_grp)

    # unpack boson thermal image
    if sensor_list["Boson_Thermal"]:
        boson_grp = sensors_grp.create_group(sensor_list[3])
        convert_boson_image(ecal_folder,boson_grp)

    # unpack audio
    if sensor_list["Wildtronics_Audio"]:
        audio_grp = sensors_grp.create_group(sensor_list[4])
        convert_wildtronics_audio(ecal_folder,audio_grp)

    # unpack radar data
    if sensor_list["TI_Radar"]:
        path_to_config = os.path.join(working_dir,"other_data","config.json")
        radar_grp = sensors_grp.create_group(sensor_list[5])
        convert_radar(ecal_folder,path_to_config,radar_grp)

    # unpack lidar PCDs
    if sensor_list["Livox_Lidar"]:
        lidar_grp = sensors_grp.create_group(sensor_list[6])
        convert_livox_point_cloud(ecal_folder,lidar_grp)

    # unpack event camera arrays
    if sensor_list["DVExplorer_Event"]:
        event_grp = sensors_grp.create_group(sensor_list[7])
        event_array_grp = event_grp.create_group("Event_Arrays")
        convert_dv_array(ecal_folder,event_array_grp)

    # unpack event camera images
    if sensor_list["DVExplorer_Event"]:
        event_image_grp = event_grp.create_group("Event_Images")
        convert_dv_image(ecal_folder,event_image_grp)
    
 
if __name__ == "__main__":
    main()