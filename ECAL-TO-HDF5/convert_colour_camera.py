
# processing imports
import numpy as np
import os
import json

import h5py
from ecal.measurement.hdf5 import Meas
import glob

import cv2
    

def convert(expNum=8, path_to_input="",filename="Color_Data",skip_confirmation=True):

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
    
    filename = filename + "_Exp{0}.hdf5".format(expNum)

    file_dict = {"NOTES_EXPR" : base_dir+"doc/description.txt",
                 "ECAL_DATA"  : base_dir+"m2s2-NUC13ANKi7/"}

    try:
        os.mkdir(os.path.join(working_dir,"output_data/"))
    except:
        pass

    ## Load source files
    print("LOAD SOURCE FILES:")
    
    # notes source 
    print("Loading experiment notes file.")
    with open(os.path.join(working_dir,path_to_input,file_dict["NOTES_EXPR"]), 'r') as file:
        data = file.read()     

    # data source 
    print("Loading data files.\n")
    ecal_folder = os.path.join(working_dir,path_to_input,file_dict["ECAL_DATA"])
    

    ## Start Conversion 
    # Create a measurement (pass either a .hdf5 file or a measurement folder)
    measurements = Meas(ecal_folder)

    # Retrieve the channels in the measurement by calling measurement.channel_names
    if filename == None:
        print("CHANNEL SELECTION: ")
        max_length = 50
        print("".join(["-"]*(max_length+6)))
        index = 0
        valid_indexs = []
        for channel_name in  measurements.get_channel_names():
            if not "_raw" in channel_name:
                index +=1
                continue
            index_text = "Channel index: %d" % index
            gap_length = max_length - len(channel_name) - 16
            gap = "".join([" "]*gap_length)
            print(channel_name,gap,"-> ", index_text )
            valid_indexs.append(index)
            index+=1
        channel_name_index = int(input("\nSelect a channel to process by choosing the index: "))
        if channel_name_index not in valid_indexs:
            print("Invalid Index Chosen. Exiting.")
            exit()
    else:
        channel_name_index = 0
        for channel_name in  measurements.get_channel_names():
            channel_descriptor = filename.lower().split("_")[0]
            if channel_descriptor in channel_name:
                break
            channel_name_index +=1

    try:
        channel_name = measurements.get_channel_names()[channel_name_index]
    except:
        print("Channel not found with given descriptor: %s" % channel_descriptor)
        print("Available Channels are: ")
        for name in measurements.get_channel_names():
            print(name)
        print("The channel descriptor must be present in channel name.")
        print("The channel descriptor is derived from the output filename.")
        exit()

    print("Channel chosen: " + channel_name)
    if skip_confirmation:
        print("CONVERTING:")
        
    else:
        cont = input("Continue [y/n]: ")
        print("\n")

        if cont == "n" or cont == "N":
            exit()
        else:
            print("CONVERTING:")


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


def main():
    convert()
    # exit()
    # for i in range(4,8):
    #     convert(i)

if __name__ == "__main__":
    main()