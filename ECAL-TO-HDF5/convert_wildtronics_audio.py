
# processing imports
import numpy as np
import os
import json

import h5py
from ecal.measurement.hdf5 import Meas
import glob

    

def convert( path_to_folder, group_handle, channel_name = "rt/audio/audio"):

    print("CONVERTING ECAL AUDIO MEASUREMENT TO HDF5:")
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
        array_size = int.from_bytes(measurements.get_entry_data(frame_id)[start:start+8],"little")
        start = start + 8
        
        # print(array_size)

        audio_chunk = np.frombuffer(measurements.get_entry_data(frame_id)[start:start+array_size],dtype=np.uint8)

        chunkGrp = dataGrp.create_group("Audio_Chunk_%s" % (frame_number))
        timeGrp = chunkGrp.create_group("Timestamps")
        timeGrp.create_dataset("nano_seconds" , data = nanosec, dtype = np.uint32)
        timeGrp.create_dataset("seconds" , data = sec, dtype = np.uint32)
        chunkGrp.create_dataset("audio_bytes",data=audio_chunk,dtype=np.uint8)

        # print progress bar
        progress_points = 50
        progress = int((frame_number)*progress_points/(number_of_frames))
        bar = "".join([u"\u2588"]*progress + [" "]*(progress_points-progress-1))
        print(" Total Progress: %d%%" % ((progress+1)*100/progress_points) + " |" + str(bar) + "| "  ,end="\r") 
        
    print("\n")

               
    paramGrp.create_dataset("bit_rate", data =128)
    paramGrp.create_dataset("number_of_channels", data =1)
    paramGrp.create_dataset("sample_rate", data =16000)
    paramGrp.create_dataset("format", data =["wave".encode("ascii")])
    paramGrp.create_dataset("sample_format", data =["S16LE".encode("ascii")])










def main():
    convert(3)
    # exit()
    # for i in range(4,8):
    #     convert(i)

if __name__ == "__main__":
    main()