
# processing imports
import numpy as np
import os
import json
import struct
import h5py
from ecal.measurement.hdf5 import Meas
import glob

import cv2
    

def convert(expNum=8, channel_name = "rt/livox/lidar", quick_convert = True):

    print("CONVERTING ECAL MEASUREMENT TO HDF5:")
    working_dir = os.path.dirname(__file__)

    # expNum = 6
    Nutramax_data = True
    if Nutramax_data:
        base_dir = "ecal_data/Exp {0}/".format(expNum)
    else:
        # print("ecal_data/Exp{0}_*".format(expNum))
        dirs = os.path.join(working_dir,"ecal_data/Exp{0}_**/".format(expNum))
        base_dir = glob.glob(dirs)[0]
        print(base_dir,end="\n\n")
    
    filename = "Livox_PointCloud_Exp{0}.hdf5".format(expNum)

    file_dict = {"NOTES_EXPR" : base_dir+ "doc/description.txt",
                 "ECAL_DATA"  : base_dir+ "m2s2-NUC13ANKi7/"}

    try:
        os.mkdir(os.path.join(working_dir,"output_data/"))
    except:
        pass

    ## Load source files
    print("LOAD SOURCE FILES:")
    
    # notes source 
    print("Loading experiment notes file.")
    with open(os.path.join(working_dir,file_dict["NOTES_EXPR"]), 'r') as file:
        data = file.read()     
    
    # data source 
    print("Loading data files.\n")
    ecal_folder = os.path.join(working_dir,file_dict["ECAL_DATA"])

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
    

    ## Start Conversion 
    # Create a measurement (pass either a .hdf5 file or a measurement folder)
    measurements = Meas(ecal_folder)



    # create 
    print("Creating output file.")
    try:
        out_file = h5py.File(os.path.join(working_dir,"output_data/%s"%(filename)),'x')
    except:
        print("An output file of that name already exists.\n")
        exit()

    # create starting hierarchy
    print("Storing LiDAR Info.\n")
    dataGrp = out_file.create_group("Data")
    paramGrp = out_file.create_group("Params")


    # Comments
    commentGrp = out_file.create_group("Comments")
    setup=[data.encode("ascii")]  
    commentGrp.create_dataset("experiment_setup", shape=(len(setup),1), data=setup) 
    
            
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
        frameGrp = dataGrp.create_group("PCD_Frame_%s" % (frame_number))
        timeGrp = frameGrp.create_group("timeStamps")
        timeGrp.create_dataset("nanosec" , data = nanosec, dtype = np.uint32)
        timeGrp.create_dataset("seconds" , data = sec, dtype = np.uint32)
        
        if quick_convert:
            pcd_bytes = np.frombuffer(measurements.get_entry_data(frame_id)[start:start+data_size],dtype=np.uint8)
            start = start+data_size
            
            frameGrp.create_dataset("PCD_Bytes",data=pcd_bytes,dtype=np.uint8)

             # print progress bar
            progress_points = 50
            progress = int((frame_number)*progress_points/(number_of_frames))
            bar = "".join([u"\u2588"]*progress + [" "]*(progress_points-progress-1))
            print("Progress: %d%%" % ((progress+1)*100/progress_points) + " |" + str(bar) + "| "  ,end="\r") 
        
        else:
            for point in range(width*height):
                
                pointGrp = frameGrp.create_group("Point_%d" % point)
                
                for field in description_of_fields:
                    field_name = field[0]
                    offset = field[1]
                    count = field[3]
                    size = field[2](count).itemsize

                    data  = struct.unpack(unpack_dict[field[2]],measurements.get_entry_data(frame_id)[start+offset:start+offset+size])[0]
                    pointGrp.create_dataset(field_name,data=data,dtype=field[2])

                start=start+point_step

                # print progress bar
                progress_points = 50
                progress = int((frame_number)*progress_points/(number_of_frames))
                bar = "".join([u"\u2588"]*progress + [" "]*(progress_points-progress-1))
                print("Frame Progess %.2f%% | " % (point*100/(width*height)),"Total Progress: %d%%" % ((progress+1)*100/progress_points) + " |" + str(bar) + "| "  ,end="\r") 
        
    print("\n")
            

    is_dense = int.from_bytes(measurements.get_entry_data(frame_id)[start:start+1],"little")
    start = start + 1


    paramGrp.create_dataset("Point_Step",data=point_step)
    paramGrp.create_dataset("Height",data=height)
    paramGrp.create_dataset("Width",data=width)
    paramGrp.create_dataset("Row_Step",data=row_step)    
    paramGrp.create_dataset("is_big_endian",data=is_big_endian)

    if quick_convert:
        
        fieldInfoGrp = paramGrp.create_group("Field_Info")
        for field in description_of_fields:
            field_name = field[0]
            fieldGrp = fieldInfoGrp.create_group("Field_%s" % field_name)
            
            offset = field[1]
            fieldGrp.create_dataset("Offset_From_Start",data=offset)

            count = field[3]
            fieldGrp.create_dataset("Number_Of_Points",data=count)

            fieldGrp.create_dataset("Field_Data_Type",data=[type_description_dict[field[2]].encode("ascii")])

            size = field[2](count).itemsize
            fieldGrp.create_dataset("Field_Size_In_Bytes",data=size)

        with open(os.path.join(working_dir,"other_data/lidar_field_info.txt"), 'r') as file:
            explanation = [file.read().encode("ascii") ]    
        paramGrp.create_dataset("Field_Info_Explanation",data=explanation)

    



def main():
    convert(3)
    # exit()
    # for i in range(4,8):
    #     convert(i)

if __name__ == "__main__":
    main()