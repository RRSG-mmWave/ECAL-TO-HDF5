
# processing imports
import numpy as np
import os
import json
import struct
import h5py
from ecal.measurement.hdf5 import Meas
import glob

import cv2
    

def convert( path_to_folder, group_handle, channel_name = "rt/livox/lidar"):

    print("CONVERTING ECAL LIDAR MEASUREMENT TO HDF5:")
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


    datatype_dict = {
        1: np.int8, 
        2: np.uint8, 
        3: np.int16,  
        4: np.uint16, 
        5: np.int32,  
        6: np.uint32, 
        7: np.float32,
        8: np.float64
    }

    unpack_dict = {
        np.int8     :"<b", 
        np.uint8    :"<B", 
        np.int16    :"<h",  
        np.uint16   :"<H", 
        np.int32    :"<l",  
        np.uint32   :"<L", 
        np.float32  :"<f",
        np.float64  :"<d"
    }

    type_description_dict = {
        np.int8     :"INT8", 
        np.uint8    :"UINT8", 
        np.int16    :"INT16",  
        np.uint16   :"UINT16", 
        np.int32    :"INT32",  
        np.uint32   :"UINT32", 
        np.float32  :"FLOAT32",
        np.float64  :"FLOAT64"
    }
    
    
            
    # get start and end frame ids
    print("BEGINNING CONVERSION:")
    number_of_frames = len(measurements.get_entries_info(channel_name))
    print("%d frames to convert" % number_of_frames)

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

        height = int.from_bytes(measurements.get_entry_data(frame_id)[start:start+4],"little")
        start = start + 4

        width = int.from_bytes(measurements.get_entry_data(frame_id)[start:start+4],"little")
        start = start + 4

        point_fields_arr_size = int.from_bytes(measurements.get_entry_data(frame_id)[start:start+8],"little")
        start=start+8
        
        description_of_fields = []

        for j in range(point_fields_arr_size):
            field_info = []
            # print("\nField Number:", i)
            string_size  = int.from_bytes(measurements.get_entry_data(frame_id)[start:start+8],"little")       
            start=start+8

            name_of_field = (measurements.get_entry_data(frame_id)[start:start+string_size]).decode("ascii")
            field_info.append(name_of_field)
            start=start+string_size

            offset = int.from_bytes(measurements.get_entry_data(frame_id)[start:start+4],"little")
            field_info.append(offset)
            start=start+4
            
            datatype = int.from_bytes(measurements.get_entry_data(frame_id)[start:start+1],"little")
            field_info.append(datatype_dict[datatype])
            start=start+1

            count = int.from_bytes(measurements.get_entry_data(frame_id)[start:start+4],"little")
            field_info.append(count)
            start=start+4

            description_of_fields.append(field_info)
        
        # for field in description_of_fields:
        #     print(field)

        is_big_endian = int.from_bytes(measurements.get_entry_data(frame_id)[start:start+1],"little")   
        start=start+1

        point_step = int.from_bytes(measurements.get_entry_data(frame_id)[start:start+4],"little")
        start=start+4

        row_step = int.from_bytes(measurements.get_entry_data(frame_id)[start:start+4],"little")
        start=start+4

        data_size = int.from_bytes(measurements.get_entry_data(frame_id)[start:start+8],"little")
        start=start+8
        
        # bytecount = 0
        # store data
        frameGrp = dataGrp.create_group("PCD_%s" % (frame_number))
        timeGrp = frameGrp.create_group("Timestamps")
        timeGrp.create_dataset("nano_seconds" , data = nanosec, dtype = np.uint32)
        timeGrp.create_dataset("seconds" , data = sec, dtype = np.uint32)

        # this code only works for a point step of 18 where we are taking the first 4 fields of 6 fields to be float32 and last fields
        # are uint8 
        pcd_bytes = np.frombuffer(measurements.get_entry_data(frame_id)[start:start+data_size],dtype=np.uint8)
        points_all_bytes = np.reshape(pcd_bytes,(width*height,point_step))
        points_xyz_intensity_bytes = points_all_bytes[:,0:-2]
        points_xyz_intensity_bytes = points_xyz_intensity_bytes.flatten()
        point_field_list = np.frombuffer(points_xyz_intensity_bytes,dtype=np.float32)
        points = np.reshape(point_field_list,(width*height,4)) 

        start = start+data_size
        
        pcd_header = "\n".join([
            "# .PCD v0.7 - Point Cloud Data file format",
            "VERSION 0.7",
            "FIELDS x y z intensity",
            "SIZE 4 4 4 4",
            "TYPE F F F F",
            "COUNT 1 1 1 1",
            "WIDTH 24000",
            "HEIGHT 1",
            "VIEWPOINT 0 0 0 1 0 0 0",
            "POINTS 24000",
            "DATA ascii",
        ])
        frameGrp.create_dataset("pcd_header",data=[pcd_header.encode("ascii")])
        frameGrp.create_dataset("pcd_data",data=points,dtype=np.float32)

            # print progress bar
        progress_points = 50
        progress = int((frame_number)*progress_points/(number_of_frames))
        bar = "".join([u"\u2588"]*progress + [" "]*(progress_points-progress-1))
        print("Progress: %d%%" % ((progress+1)*100/progress_points) + " |" + str(bar) + "| "  ,end="\r") 
    
                
    print("\n")
            

    is_dense = int.from_bytes(measurements.get_entry_data(frame_id)[start:start+1],"little")
    start = start + 1


    paramGrp.create_dataset("point_step",data=point_step)
    paramGrp.create_dataset("height",data=height)
    paramGrp.create_dataset("width",data=width)
    paramGrp.create_dataset("row_step",data=row_step)    
    paramGrp.create_dataset("is_big_endian",data=is_big_endian)
        