
# processing imports
import numpy as np
import os
import json

import h5py
from ecal.measurement.hdf5 import Meas
import glob

import cv2
    

def convert(expNum=8, channel_name = "rt/dv/events",quick_convert = True):

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
    
    filename = "DVEvent_Arrays_Exp{0}.hdf5".format(expNum)

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

    print(measurements.get_channel_type(channel_name))


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
        num_y_pixels = int.from_bytes(measurements.get_entry_data(frame_id)[start:start+4],"little")
        start = start + 4

        num_x_pixels = int.from_bytes(measurements.get_entry_data(frame_id)[start:start+4],"little")
        start = start + 4

        number_of_events = int.from_bytes(measurements.get_entry_data(frame_id)[start:start+8],"little")
        array_szie = number_of_events*(2+2+4+4+1)
        start = start + 8

        # store data
        frameGrp = dataGrp.create_group("Event_Array_%s" % (frame_number))
        timeGrp = frameGrp.create_group("timeStamps")
        timeGrp.create_dataset("nanosec" , data = nanosec, dtype = np.uint32)
        timeGrp.create_dataset("seconds" , data = sec, dtype = np.uint32)
        
        if quick_convert:
            array_bytes = np.frombuffer(measurements.get_entry_data(frame_id)[start:start+array_szie],dtype=np.uint8)
            start = start+array_szie
            
            frameGrp.create_dataset("Event_Array_Bytes",data=array_bytes,dtype=np.uint8)
            frameGrp.create_dataset("Number_of_Events",data=number_of_events,dtype=np.uint64)


             # print progress bar
            progress_points = 50
            progress = int((frame_number)*progress_points/(number_of_frames))
            bar = "".join([u"\u2588"]*progress + [" "]*(progress_points-progress-1))
            print("Progress: %d%%" % ((progress+1)*100/progress_points) + " |" + str(bar) + "| "  ,end="\r") 
        
        else:        
            for event in range(number_of_events):
                event_group = frameGrp.create_group("Event_%d" % event)
                x = int.from_bytes(measurements.get_entry_data(frame_id)[start:start+2],"little")
                event_group.create_dataset("x",data=x,dtype=np.uint16)
                start = start + 2 

                y = int.from_bytes(measurements.get_entry_data(frame_id)[start:start+2],"little")
                event_group.create_dataset("y",data=y,dtype=np.uint16)
                start = start + 2 

                event_sec = int.from_bytes(measurements.get_entry_data(frame_id)[start:start+4],"little")
                event_group.create_dataset("time_seconds",data=event_sec,dtype=np.uint32)
                start = start + 4

                event_nanosec = int.from_bytes(measurements.get_entry_data(frame_id)[start:start+4],"little")
                event_group.create_dataset("time_nanoseconds",data=event_nanosec,dtype=np.uint32)
                start = start + 4

                polarity = int.from_bytes(measurements.get_entry_data(frame_id)[start:start+1],"little")
                event_group.create_dataset("polarity",data=polarity,dtype=np.uint8)
                start = start + 1


            #print progress bar
                progress_points = 50
                progress = int((frame_number)*progress_points/(number_of_frames))
                bar = "".join([u"\u2588"]*progress + [" "]*(progress_points-progress-1))
                print("Event Array Progress %.2f%% |" % (100*event/number_of_events)," Total Progress: %d%%" % ((progress+1)*100/progress_points) + " |" + str(bar) + "| "  ,end="\r") 
        
    print("\n")

               
    coordinateSizeGrp = paramGrp.create_group("co_ordinates")
    coordinateSizeGrp.create_dataset("x_width",data=num_x_pixels)
    coordinateSizeGrp.create_dataset("y_height",data=num_y_pixels)

    if quick_convert:
        
        with open(os.path.join(working_dir,"other_data/event_array_info.txt"), 'r') as file:
            explanation = [file.read().encode("ascii") ]    
        paramGrp.create_dataset("Event_Array_Explanation",data=explanation)



def main():
    convert(3)
    # exit()
    # for i in range(4,8):
    #     convert(i)

if __name__ == "__main__":
    main()