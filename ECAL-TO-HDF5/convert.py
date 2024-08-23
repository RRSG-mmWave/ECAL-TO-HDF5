# processing imports
import numpy as np
import os
import json

import h5py
from ecal.measurement.hdf5 import Meas
import glob

import cv2

def convert_radar(file_dict, output_file, measurements):
    ## Load source files
    print("LOAD SOURCE FILES:")
    working_dir = os.path.dirname(__file__)

    # parameter source file
    # sort = True
    try:
        f = open(os.path.join(working_dir,file_dict["RADAR_PARAM_JSON"]))
        print("Loading parameter json file.")
        configDict = json.load(f)
        f.close()
    except:
        print("No Parameter File Found.")
        exit()

    print(json.dumps(configDict, indent=4))
    # create starting hierarchy
    radar_data = output_file.create_group("Radar data")

    print("\nStoring radar data.")
    dataGrp = radar_data.create_group("Data")
    paramGrp = radar_data.create_group("Params")

    profileCfgGrp = paramGrp.create_group("profileCfg")
    for key in configDict["profileCfg"]:
        profileCfgGrp.create_dataset(key,data=configDict["profileCfg"][key])

    frameCfgGrp = paramGrp.create_group("frameCfg")
    for key in configDict["frameCfg"]:
        frameCfgGrp.create_dataset(key,data=configDict["frameCfg"][key])

    channelCfgGrp = paramGrp.create_group("channelCfg")
    for key in configDict["channelCfg"]:
        channelCfgGrp.create_dataset(key,data=configDict["channelCfg"][key])

    adcCfgGrp = paramGrp.create_group("adcCfg")
    for key in configDict["adcCfg"]:
        adcCfgGrp.create_dataset(key,data=configDict["adcCfg"][key])

    adcbufCfgGrp = paramGrp.create_group("adcbufCfg")
    for key in configDict["adcbufCfg"]:
        adcbufCfgGrp.create_dataset(key,data=configDict["adcbufCfg"][key])

    # Comments
    commentGrp = radar_data.create_group("Comments")
    radar=["AWR1642BOOST".encode("ascii")]
    radarTypeDSet = commentGrp.create_dataset("radar_type", shape=(len(radar),1), data=radar)    
    #setup=[exp_notes.encode("ascii")]  
    #setupCommentsDSet = commentGrp.create_dataset("experiment_setup", shape=(len(setup),1), data=setup) 

    #radar data channel name
    channel_name = "rt/radar_data"
    
    # get start and end frame ids
    # start_frame =  measurements.get_entries_info(channel_name)[0]["id"]
    # end_frame =  measurements.get_entries_info(channel_name)[-1]["id"]
    number_of_frames = len(measurements.get_entries_info(channel_name))
    print("Number of frames: %d"%(number_of_frames))

    for i, entry_info in enumerate(measurements.get_entries_info(channel_name)):
        # extract frame id
        frame_number = i

        frame_id = entry_info["id"]

        sec = int.from_bytes(measurements.get_entry_data(frame_id)[0:4],"little")
        nanosec = int.from_bytes(measurements.get_entry_data(frame_id)[4:8],"little")
        string_size = int.from_bytes(measurements.get_entry_data(frame_id)[8:16],"little")

        # print("Frame ID " + (measurements.get_entry_data(frame_id)[16:16+string_size]).decode("ascii"))

        # start of message
        start = 16+string_size
        frame_size = int.from_bytes(measurements.get_entry_data(frame_id)[start:start+4],"little")
        data_size =   int.from_bytes(measurements.get_entry_data(frame_id)[start+4:start+4+8],"little")
        if not (frame_size == data_size):
            print("Data size and expected frame size do not match")
            exit()

        # extract frame data
        bytes = measurements.get_entry_data(frame_id)[start+4+8:]
        if not (len(bytes) == data_size):
            print("Data size and size of data extracted do not matchh")
            exit()

        # convert to uint16 samples
        frame = np.frombuffer(bytes, dtype=np.int16)
        
        # store data
        frameGrp = dataGrp.create_group("Frame_%s" % (frame_number))
        timeGrp = frameGrp.create_group("timeStamps")
        nsecDs = timeGrp.create_dataset("nanosec" , data = nanosec, dtype = np.uint32)
        secsDs = timeGrp.create_dataset("seconds" , data = sec, dtype = np.int32)
        frameGrp.create_dataset("frameData",data=frame,dtype=np.int16)

        # print progress bar
        progress_points = 50
        progress = int((frame_number)*progress_points/(number_of_frames))
        bar = "".join([u"\u2588"]*progress + [" "]*(progress_points-progress-1))
        print("Progress: %d%%" % ((progress+1)*100/progress_points) + " |" + str(bar) + "| "  ,end="\r")
        
    print("\n")


def convert_camera(file_dict, output_file, measurements):
    # create starting hierarchy
    camera_grp = output_file.create_group("Camera data")

    try:
        convert_color(camera_grp, measurements)
    except Exception as e:
        print(f"An error occurred: {e}")

    try:
        convert_depth(camera_grp, measurements)
    except Exception as e:
        print(f"An error occurred: {e}")

def convert_color(camera_grp, measurements):
    channel_name = "rt/camera/color/image_raw"

    color_images = camera_grp.create_group("Color images")

    # create starting hierarchy
    print("\nStoring color data.")
    dataGrp = color_images.create_group("Data")
    paramGrp = color_images.create_group("Params")

    number_of_frames = len(measurements.get_entries_info(channel_name))
    print("Number of frames: %d"%(number_of_frames))

    for i, entry_info in  enumerate(measurements.get_entries_info(channel_name)):

        # extract frame id
        frame_number = i

        frame_id = entry_info["id"]

        sec = int.from_bytes(measurements.get_entry_data(frame_id)[0:4],"little")
        nanosec = int.from_bytes(measurements.get_entry_data(frame_id)[4:8],"little")
        string_size = int.from_bytes(measurements.get_entry_data(frame_id)[8:16],"little")

        # print("Frame ID " + (measurements.get_entry_data(frame_id)[16:16+string_size]).decode("ascii"))

        ## start of message
        # image size
        start = 16+string_size
        height = int.from_bytes(measurements.get_entry_data(frame_id)[start:start+4],"little")
        # print("Height: %d" % height)
        
        start = start + 4
        width = int.from_bytes(measurements.get_entry_data(frame_id)[start:start+4],"little")
        # print("Width: %d" % width)
        
        # image encoding
        start = start + 4
        string_size = int.from_bytes(measurements.get_entry_data(frame_id)[start:start+8],"little")
        start = start + 8
        encoding = (measurements.get_entry_data(frame_id)[16:16+string_size]).decode("utf-8")
        # print("Encoding: %s" % encoding)

        start = start + string_size
        is_big_endian = int.from_bytes(measurements.get_entry_data(frame_id)[start:start+1],"little")
        # print("Big endian? %d" % is_big_endian)

        start = start + 1
        row_length = int.from_bytes(measurements.get_entry_data(frame_id)[start:start+4],"little")
        # print("Row Length in bytes: %d" % row_length)

        start = start + 4
        image_size_in_bytes = int.from_bytes(measurements.get_entry_data(frame_id)[start:start+8],"little")
        # print("Image is %d bytes." % image_size_in_bytes)

        start = start + 8
        data = measurements.get_entry_data(frame_id)[start:]
        byte_list = np.frombuffer(data,dtype=np.uint8)
        image_arr = np.reshape(byte_list,newshape=(height,width,3), order="C")
        im_rgb = cv2.cvtColor(image_arr, cv2.COLOR_BGR2RGB)

        # store data
        frameGrp = dataGrp.create_group("Frame_%s" % (frame_number))
        timeGrp = frameGrp.create_group("timeStamps")
        timeGrp.create_dataset("nanosec" , data = nanosec, dtype = np.uint32)
        timeGrp.create_dataset("seconds" , data = sec, dtype = np.uint32)
        frameGrp.create_dataset("frameData",data= im_rgb,shape=(height,width,3),dtype=np.uint8)

        # print progress bar
        progress_points = 50
        progress = int((frame_number)*progress_points/(number_of_frames))
        bar = "".join([u"\u2588"]*progress + [" "]*(progress_points-progress-1))
        print("Progress: %d%%" % ((progress+1)*100/progress_points) + " |" + str(bar) + "| "  ,end="\r") 

    print("\n")
    imageSizeGrp = paramGrp.create_group("image_size")
    imageSizeGrp.create_dataset("width",data=width)
    imageSizeGrp.create_dataset("height",data=height)

    encodingGrp = paramGrp.create_group("image_encoding_info")
    encodingGrp.create_dataset("is_big_endian",data=is_big_endian)
    encodingGrp.create_dataset("row_length",data=row_length)

def convert_depth(camera_grp, measurements):
    channel_name = "rt/camera/aligned_depth_to_color/image_raw"

    depth_images = camera_grp.create_group("Depth images")

    # create starting hierarchy
    print("\nStoring depth data.")
    dataGrp = depth_images.create_group("Data")
    paramGrp = depth_images.create_group("Params")

    number_of_frames = len(measurements.get_entries_info(channel_name))
    print("Number of frames: %d"%(number_of_frames))

    for i, entry_info in  enumerate(measurements.get_entries_info(channel_name)):

        # extract frame id
        frame_number = i

        frame_id = entry_info["id"]

        sec = int.from_bytes(measurements.get_entry_data(frame_id)[0:4],"little")
        nanosec = int.from_bytes(measurements.get_entry_data(frame_id)[4:8],"little")
        string_size = int.from_bytes(measurements.get_entry_data(frame_id)[8:16],"little")

        # print("Frame ID " + (measurements.get_entry_data(frame_id)[16:16+string_size]).decode("ascii"))

        ## start of message
        # image size
        start = 16+string_size
        height = int.from_bytes(measurements.get_entry_data(frame_id)[start:start+4],"little")
        # print("Height: %d" % height)
        
        start = start + 4
        width = int.from_bytes(measurements.get_entry_data(frame_id)[start:start+4],"little")
        # print("Width: %d" % width)
        
        # image encoding
        start = start + 4
        string_size = int.from_bytes(measurements.get_entry_data(frame_id)[start:start+8],"little")
        start = start + 8
        encoding = (measurements.get_entry_data(frame_id)[16:16+string_size]).decode("utf-8")
        # print("Encoding: %s" % encoding)

        start = start + string_size
        is_big_endian = int.from_bytes(measurements.get_entry_data(frame_id)[start:start+1],"little")
        # print("Big endian? %d" % is_big_endian)

        start = start + 1
        row_length = int.from_bytes(measurements.get_entry_data(frame_id)[start:start+4],"little")
        # print("Row Length in bytes: %d" % row_length)

        start = start + 4
        image_size_in_bytes = int.from_bytes(measurements.get_entry_data(frame_id)[start:start+8],"little")
        # print("Image is %d bytes." % image_size_in_bytes)

        start = start + 8
        data = measurements.get_entry_data(frame_id)[start:]
        byte_list = np.frombuffer(data,dtype=np.uint16)
        image_arr = np.reshape(byte_list,newshape=(height,width), order="C")

        # store data
        frameGrp = dataGrp.create_group("Frame_%s" % (frame_number))
        timeGrp = frameGrp.create_group("timeStamps")
        timeGrp.create_dataset("nanosec" , data = nanosec, dtype = np.uint32)
        timeGrp.create_dataset("seconds" , data = sec, dtype = np.int32)
        frameGrp.create_dataset("frameData",data= image_arr,shape=(height,width),dtype=np.int16)

        # print progress bar
        progress_points = 50
        progress = int((frame_number)*progress_points/(number_of_frames))
        bar = "".join([u"\u2588"]*progress + [" "]*(progress_points-progress-1))
        print("Progress: %d%%" % ((progress+1)*100/progress_points) + " |" + str(bar) + "| "  ,end="\r") 
    
    print("\n")

    imageSizeGrp = paramGrp.create_group("image_size")
    imageSizeGrp.create_dataset("width",data=width)
    imageSizeGrp.create_dataset("height",data=height)

    encodingGrp = paramGrp.create_group("image_encoding_info")
    encodingGrp.create_dataset("is_big_endian",data=is_big_endian)
    encodingGrp.create_dataset("row_length",data=row_length)

def list_files_and_folders(path):
    try:
        items = os.listdir(path)
        return items
    except Exception as e:
        print(f"Error: {e}")
        return []

def pick_file(files):
    # Display the list of files and folders
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
                print("Invalid selection. Please choose a valid number from the list.")
        except ValueError:
            print("Please enter a valid number.")

    return files[choice-1]

def output_filename(filename):
    # Split the filename at the dot
    base, _ = filename.split('.')
    
    # Remove the "_measurement" part
    base = base.replace("_measurement", "")
    
    # Add the prefix and the new extension
    output_filename = "Experiment_" + base + ".hdf5"
    
    return output_filename

def main():
    print("CONVERTING ECAL MEASUREMENT TO HDF5:")
    working_dir = os.path.dirname(__file__)


    data_path = "/home/mmwave/ssd/RRSG/ros2_ws/ecal_data/"
    data_folders = list_files_and_folders(data_path)


    if not data_folders:
        print("No files or folders found in the directory.")
        return

    data_file_choice = pick_file(data_folders)
    

    radar_config_path = "other_data/"
    radar_configs = list_files_and_folders(radar_config_path)

    if not radar_configs:
        print("No radar configs found in the directory.")
        return

    radar_config_choice = pick_file(radar_configs)
    
    radar_config_dir = os.path.join(radar_config_path, radar_config_choice)


    #ecal_measurement_dir = "/home/mmwave/RRSG/ros2_ws/ecal_data/2023-08-07_14-17-34.153_measurement/"
    ecal_measurement_dir = os.path.join(data_path, data_file_choice)
    #print(ecal_measurement_dir)
    base_dir = glob.glob(ecal_measurement_dir)[0]
    print(f"Ecal Measurement folder: {base_dir}")

    #output_file_name = "Experiment_2023-08-04_15-05-49.hdf5"
    output_file_name = output_filename(data_file_choice)
    print("Output file: ", output_file_name)

    file_dict = {"RADAR_PARAM_JSON" : radar_config_dir,
                 "NOTES_EXPR" : base_dir+"/doc/description.txt",
                 "ECAL_DATA"  : base_dir+"/mmwave/"}

    try:
        os.mkdir(os.path.join(working_dir,"output_data/"))
    except:
        pass

    # notes source 
    print("Loading experiment notes file.")
    with open(file_dict["NOTES_EXPR"], 'r') as file:
        exp_notes = file.read()     

    # data source 
    #print("Loading data files.\n")
    #ecal_folder = os.path.join(working_dir,file_dict["ECAL_DATA"])
    print(file_dict["ECAL_DATA"])

    # create 
    print("CREATING OUTPUT FILE:")
    try:
        output_file = h5py.File(os.path.join(working_dir,"output_data/%s"%(output_file_name)),'w')
    except Exception as e:
        print(e)

    # Experimetal set up
    exp_setup = output_file.create_group("Experimental setup")   
    setup=[exp_notes.encode("ascii")]  
    setupCommentsDSet = exp_setup.create_dataset("experiment_setup", shape=(len(setup),1), data=setup)

    print("CONVERTING:")
    measurements = Meas(file_dict["ECAL_DATA"])

    channel_names = measurements.get_channel_names()
    print("Available channels: %s"%(channel_names))

    convert_radar(file_dict,output_file,measurements)
    convert_camera(file_dict,output_file,measurements)



if __name__ == "__main__":
    main()
