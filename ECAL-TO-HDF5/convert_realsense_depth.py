
# processing imports
import numpy as np
import os
import json

import h5py
from ecal.measurement.hdf5 import Meas
import glob

import cv2
    

def convert(path_to_folder,group_handle, channel_name="rt/camera/depth/image_rect_raw"):

    print("CONVERTING ECAL REALSENSE DEPTH MEASUREMENT TO HDF5:")
    working_dir = os.path.dirname(__file__)
    
    try:
        os.mkdir(os.path.join(working_dir,"output_data/"))
    except:
        pass

    ## Load source files
    print("LOAD SOURCE FILES:")
    

    # data source 
    ecal_folder = os.path.join(path_to_folder)
    print("Done.\n")


    ## Start Conversion 
    measurements = Meas(ecal_folder)


    # create starting hierarchy
    dataGrp = group_handle.create_group("Data")
    paramGrp = group_handle.create_group("Parameters")
            
    # get start and end frame ids
    number_of_frames = len(measurements.get_entries_info(channel_name))
    print("%d frames to convert" % number_of_frames)

    i = 0
    for entry_info in  measurements.get_entries_info(channel_name):

        # extract frame id
        frame_number = i  
        i+=1

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
        frameGrp = dataGrp.create_group("Image_%s" % (frame_number))
        timeGrp = frameGrp.create_group("Timestamps")
        timeGrp.create_dataset("nano_seconds" , data = nanosec, dtype = np.uint32)
        timeGrp.create_dataset("seconds" , data = sec, dtype = np.uint32)
        frameGrp.create_dataset("image_data",data= image_arr,shape=(height,width),dtype=np.int16)

        # print progress bar
        progress_points = 50
        progress = int((frame_number)*progress_points/(number_of_frames))
        bar = "".join([u"\u2588"]*progress + [" "]*(progress_points-progress-1))
        print("Progress: %d%%" % ((progress+1)*100/progress_points) + " |" + str(bar) + "| "  ,end="\r") 
    
    print("\n")

    imageSizeGrp = paramGrp.create_group("Image_Size")
    imageSizeGrp.create_dataset("width",data=width)
    imageSizeGrp.create_dataset("height",data=height)
    imageSizeGrp.create_dataset("number_of_channels",data=1)

    encodingGrp = paramGrp.create_group("Image_Encoding_Info")
    encodingGrp.create_dataset("is_big_endian",data=is_big_endian)
    encodingGrp.create_dataset("row_length",data=row_length)


