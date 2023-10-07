
# processing imports
import numpy as np
import os
import json

import h5py
from ecal.measurement.hdf5 import Meas
import glob

import cv2
    

def convert(expNum=8, channel_name = "rt/dvs_rendering"):

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
    
    filename = "DVEvent_Image_Exp{0}.hdf5".format(expNum)

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
    

    ## Start Conversion 
    # Create a measurement (pass either a .hdf5 file or a measurement folder)
    measurements = Meas(ecal_folder)


    # create 
    print("Creating output file")
    try:
        out_file = h5py.File(os.path.join(working_dir,"output_data/%s"%(filename)),'x')
    except:
        print("An output file of that name already exists.\n")

    # create starting hierarchy
    print("Storing config data.\n")
    dataGrp = out_file.create_group("Data")
    paramGrp = out_file.create_group("Params")


    # Comments
    commentGrp = out_file.create_group("Comments")
    setup=[data.encode("ascii")]  
    commentGrp.create_dataset("experiment_setup", shape=(len(setup),1), data=setup) 
            
    # get start and end frame ids
    start_frame =  measurements.get_entries_info(channel_name)[0]["id"]
    end_frame =  measurements.get_entries_info(channel_name)[-1]["id"]
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
        # encoding = (measurements.get_entry_data(frame_id)[16:16+string_size]).decode("utf-8")
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


def main():
    convert(3)
    # exit()
    # for i in range(4,8):
    #     convert(i)

if __name__ == "__main__":
    main()