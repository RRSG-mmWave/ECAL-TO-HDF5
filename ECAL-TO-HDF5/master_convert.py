## Cameras
# misc
#from convert_ximea_camera import convert as convert_ximea_raw
#from convert_boson_image import convert as convert_boson_image

# realsense
from convert_realsense_depth import convert as convert_realsense_depth
from convert_realsense_colour import convert as convert_realsense_colour

# event camera
#from convert_dv_event_array import convert as convert_dv_array
#from convert_dv_image import convert as convert_dv_image

## other sensors
from convert_radar import convert as convert_radar
#from convert_wildtronics_audio import convert as convert_wildtronics_audio
#from convert_livox_point_cloud import convert as convert_livox_point_cloud


from ecal.measurement.hdf5 import Meas

import os
import glob
import h5py
import numpy as np

def list_files_and_folders(path):
    try:
        items = os.listdir(path)
        return items
    except Exception as e:
        print(f"Error: {e}")
        return []

def pick_files(files):
    # Display the list of files and folders
    files.sort()
    files = np.array(files)
    for idx, item in enumerate(files, 1):
        print(f"{idx}. {item}")

    # Ask the user to select an item
    while True:
        try:
            start_file = int(input("\nSelect the number corresponding to the first file you want to operate on: "))
            end_file = int(input("\nSelect the number corresponding to the last file you want to operate on: "))
            
            #choice = int(input("\nSelect the number corresponding to the file/folder you want to operate on: "))
            #if 1 <= choice <= len(files):
                #print(f"You selected: {files[choice-1]}")
                #break
            
            if 1 <= start_file <= len(files) and 1 <= end_file <= len(files) and start_file <= end_file:
                print(f"You selected: {files[start_file-1:end_file]}")
                break
            else:
                print("Invalid selection. Please choose valid numbers from the list.")
                
        except ValueError:
            print("Please enter a valid number.")

    #return files[choice-1]
    return files[start_file-1:end_file]

def pick_file(files):
    # Display the list of files and folders
    files.sort()
    files = np.array(files)
    for idx, item in enumerate(files, 1):
        print(f"{idx}. {item}")

    # Ask the user to select an item
    while True:
        try:
            choice = int(input("\nSelect the number corresponding to the file/folder you want to operate on: "))
            if 1 <= choice <= len(files):
                print(f"You selected: {files[choice-1]}")
                break

            else:
                print("Invalid selection. Please choose valid numbers from the list.")
                
        except ValueError:
            print("Please enter a valid number.")

    return files[choice-1]

def output_filename(filename):
    # Split the filename at the dot
    base, front = filename.split('.')
    
    # Remove the "_measurement" part
    #front = front.replace("_drones", "")
    
    # Add the prefix and the new extension
    output_filename = "Experiment_" + base + "_" + front + ".hdf5"
    
    return output_filename

def get_channel_names(path_to_folder):
    
    measurements = Meas(path_to_folder)
    channel_names = measurements.get_channel_names()
    return channel_names

def main(): 

    print("ECAL TO HDF5 CONVERSION:")
    print()

    #data_path = "/home/mmwave/ssd/RRSG/ros2_ws/ecal_data/"
    data_path = "/home/mmwave/ssd/ecal_meas/15-08-2024_undergrad_testset"
    #data_path = "/media/mmwave/Ventoy/data"
    data_folders = list_files_and_folders(data_path)

    if not data_folders:
        print("No files or folders found in the directory.")
        return

    data_file_choices = pick_files(data_folders)
    for data_file_choice in data_file_choices:
        output_file_name = output_filename(data_file_choice)
        print("Output file: ", output_file_name)

        # Specify data path and output names if you wish to hard code them
        base_dir = data_path
        measurement_name = data_file_choice
        host_username = "mmwave/" # it found as a sub dir of ecal meas folder 
        filename = output_file_name #output filename
    
        # use this map to enable sensors 
        sensor_list = {
            "Realsense_Colour"  :   True,
            "Realsense_Depth"   :   True,
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
            os.mkdir(os.path.join(working_dir,"output_data/"))
        except:
            pass

        try:
            out_file = h5py.File(os.path.join(working_dir,"output_data/%s"%(filename)),'w')
        except Exception as e:
            print(e)
            choice = str(input("An output file of that name already exists, would you like to override, y/n?\n"))
            choice = choice.lower()

            if choice == "y" or choice == "yes":
                try:
                    out_file = h5py.File(os.path.join(working_dir,"output_data/%s"%(filename)),'w')
                except:
                    pass
            exit()
    
        commentGrp = out_file.create_group("Comments")
        #setup=[data.encode("ascii")]
        setup=[data.encode("utf-8")]  
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
            rs_colour_grp = sensors_grp.create_group(list(sensor_list)[0])
            convert_realsense_colour(ecal_folder,rs_colour_grp)

        # unpack realsense depth
        if sensor_list["Realsense_Depth"]:
            rs_depth_grp = sensors_grp.create_group(list(sensor_list)[1])
            convert_realsense_depth(ecal_folder,rs_depth_grp)

        # unpack ximea raw image
        if sensor_list["Ximea_Raw"]:
            ximea_grp = sensors_grp.create_group(list(sensor_list)[2])
            convert_ximea_raw(ecal_folder,ximea_grp)

        # unpack boson thermal image
        if sensor_list["Boson_Thermal"]:
            boson_grp = sensors_grp.create_group(list(sensor_list)[3])
            convert_boson_image(ecal_folder,boson_grp)

        # unpack audio
        if sensor_list["Wildtronics_Audio"]:
            audio_grp = sensors_grp.create_group(list(sensor_list)[4])
            convert_wildtronics_audio(ecal_folder,audio_grp)

        # unpack radar data
        if sensor_list["TI_Radar"]:
            radar_config_path = "other_data/"
            radar_configs = list_files_and_folders(radar_config_path)

            if not radar_configs:
                print("No radar configs found in the directory.")
                return

            radar_config_choice = pick_file(radar_configs)

            path_to_config = os.path.join(working_dir,radar_config_path,radar_config_choice)

            radar_grp = sensors_grp.create_group(list(sensor_list)[5])
            convert_radar(ecal_folder,path_to_config,radar_grp)

        # unpack lidar PCDs
        if sensor_list["Livox_Lidar"]:
            lidar_grp = sensors_grp.create_group(list(sensor_list)[6])
            convert_livox_point_cloud(ecal_folder,lidar_grp)

        # unpack event camera arrays
        if sensor_list["DVExplorer_Event"]:
            event_grp = sensors_grp.create_group(list(sensor_list)[7])
            event_array_grp = event_grp.create_group("Event_Arrays")
            convert_dv_array(ecal_folder,event_array_grp)

        # unpack event camera images
        if sensor_list["DVExplorer_Event"]:
            event_image_grp = event_grp.create_group("Event_Images")
            convert_dv_image(ecal_folder,event_image_grp)
    
if __name__ == "__main__":
    main()
