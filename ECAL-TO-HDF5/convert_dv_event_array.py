
# processing imports
import numpy as np
import os
import json

import h5py
from ecal.measurement.hdf5 import Meas
import glob

import cv2
    

def convert(path_to_folder,group_handle, channel_name = "rt/dv/events"):

    print("CONVERTING ECAL EVENT ARRAY MEASUREMENT TO HDF5:")
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
    print("Frames to convert:", number_of_frames)

    # print(measurements.get_channel_type(channel_name))

    i = 0
    for entry_info in  measurements.get_entries_info(channel_name):

        # extract frame id
        frame_number = i  
        i+=1

        frame_id = entry_info["id"]

        sec = int.from_bytes(measurements.get_entry_data(frame_id)[0:4],"little")
        nanosec = int.from_bytes(measurements.get_entry_data(frame_id)[4:8],"little")
        string_size = int.from_bytes(measurements.get_entry_data(frame_id)[8:16],"little")
        start = 16+string_size


        # print("Frame ID " + (measurements.get_entry_data(frame_id)[16:16+string_size]).decode("ascii"))

        ## start of message
        # image size
        num_y_pixels = int.from_bytes(measurements.get_entry_data(frame_id)[start:start+4],"little")
        start = start + 4

        num_x_pixels = int.from_bytes(measurements.get_entry_data(frame_id)[start:start+4],"little")
        start = start + 4

        number_of_events = int.from_bytes(measurements.get_entry_data(frame_id)[start:start+8],"little")
        event_byte_size = 2+2+4+4+1
        array_szie = number_of_events*event_byte_size
        start = start + 8

        # store data
        frameGrp = dataGrp.create_group("Array_%s" % (frame_number))
        timeGrp = frameGrp.create_group("Timestamps")
        timeGrp.create_dataset("nano_seconds" , data = nanosec, dtype = np.uint32)
        timeGrp.create_dataset("seconds" , data = sec, dtype = np.uint32)
        
        array_bytes = np.frombuffer(measurements.get_entry_data(frame_id)[start:start+array_szie],dtype=np.uint8)
        bytes_per_event = np.reshape(array_bytes,(number_of_events,event_byte_size))
        
        xy_per_event = np.reshape(np.frombuffer(bytes_per_event[:,0:4].flatten(),dtype=np.uint16),(number_of_events,2))
        timestamp_per_event =  np.reshape(np.frombuffer(bytes_per_event[:,4:12].flatten(),dtype=np.uint32),(number_of_events,2))
        polarity_per_event = np.reshape(bytes_per_event[:,12:],(number_of_events,1))

        start = start+array_szie
        
        frameGrp.create_dataset("events_xy",data=xy_per_event,dtype=np.uint16)
        frameGrp.create_dataset("events_seconds",data=timestamp_per_event[:,0],dtype=np.uint32)
        frameGrp.create_dataset("events_nano_seconds",data=timestamp_per_event[:,1],dtype=np.uint32)
        frameGrp.create_dataset("events_polarity",data=polarity_per_event,dtype=np.uint8)
        frameGrp.create_dataset("number_of_events",data=number_of_events,dtype=np.uint64)


        # print progress bar
        progress_points = 50
        progress = int((frame_number)*progress_points/(number_of_frames))
        bar = "".join([u"\u2588"]*progress + [" "]*(progress_points-progress-1))
        print("Progress: %d%%" % ((progress+1)*100/progress_points) + " |" + str(bar) + "| "  ,end="\r") 
         
    print("\n")

    coordinateSizeGrp = paramGrp.create_group("co_ordinates")
    coordinateSizeGrp.create_dataset("x_width",data=num_x_pixels)
    coordinateSizeGrp.create_dataset("y_height",data=num_y_pixels)

