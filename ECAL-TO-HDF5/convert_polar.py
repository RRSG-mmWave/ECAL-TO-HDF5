
# processing imports
import numpy as np
import os
import json
import struct
import h5py
from ecal.measurement.hdf5 import Meas
import glob
    
def convert(expNum=6, index=None, path_to_input="",filename="Polar_Data"):

    print("CONVERTING ECAL MEASUREMENT TO HDF5:")
    working_dir = os.path.dirname(__file__)

    # expNum = 6
    Nutramax_data = False
    if Nutramax_data:
        base_dir = "ecal_data/Exp {0}/".format(expNum)
    else:
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
    working_dir = os.path.dirname(__file__)

    # notes source 
    print("Loading experiment notes file.")
    with open(os.path.join(working_dir,path_to_input,file_dict["NOTES_EXPR"]), 'r') as file:
        data = file.read()     

    # data source 
    print("Loading data files.\n")
    ecal_folder = os.path.join(working_dir,path_to_input,file_dict["ECAL_DATA"])

    # create 
    print("CREATING OUTPUT FILE:")
    try:
        out_file = h5py.File(os.path.join(working_dir,"output_data/%s"%(filename)),'x')
    except:
        print("An output file of that name already exists.\n")

    
    ## Start Accel Conversion 
    # Create a measurement (pass either a .hdf5 file or a measurement folder)
    measurements = Meas(ecal_folder)

    channel_names = []
    for channel_name in  measurements.get_channel_names():
        channel_descriptor = filename.lower().split("_")[0]
        if channel_descriptor in channel_name:
            print(channel_name)
            channel_names.append(channel_name)

    # create starting hierarchy
    print("Storing config data.\n")
    accelGrp = out_file.create_group("Accelerometer Data")
    ibeatGrp = out_file.create_group("Heart Rate Data")

    # Comments
    commentGrp = out_file.create_group("Comments")
    setup=[data.encode("ascii")]  
    setupCommentsDSet = commentGrp.create_dataset("experiment_setup", shape=(len(setup),1), data=setup) 

    
    # get start and end frame ids
    start_frame =  measurements.get_entries_info(channel_names[0])[0]["id"]
    end_frame =  measurements.get_entries_info(channel_names[0])[-1]["id"]
    number_of_frames = len(measurements.get_entries_info(channel_names[0]))

    i = 0
    print("Extracting Accelerometer data:")
    for entry_info in  measurements.get_entries_info(channel_names[0]):

        # extract frame id
        frame_number = i  
        i+=1

        frame_id = entry_info["id"]

        sec = int.from_bytes(measurements.get_entry_data(frame_id)[0:4],"little")
        nanosec = int.from_bytes(measurements.get_entry_data(frame_id)[4:8],"little")
        string_size = int.from_bytes(measurements.get_entry_data(frame_id)[8:16],"little")

        # print("Frame ID " + (measurements.get_entry_data(frame_id)[16:16+string_size]).decode("ascii"))

        # start of message
        start = 16+string_size
        accel_size = 2
        x = int.from_bytes(measurements.get_entry_data(frame_id)[start:start+accel_size],"little")

        start = start + accel_size
        y = int.from_bytes(measurements.get_entry_data(frame_id)[start:start+accel_size],"little")
        
        start = start + accel_size
        z = int.from_bytes(measurements.get_entry_data(frame_id)[start:start+accel_size],"little")
        
        # store data
        sampleGrp = accelGrp.create_group("Sample_%s" % (frame_number))
        timeGrp = sampleGrp.create_group("timeStamps")
        nsecDs = timeGrp.create_dataset("nanosec" , data = nanosec, dtype = np.uint32)
        secsDs = timeGrp.create_dataset("seconds" , data = sec, dtype = np.uint32)
        sampleGrp.create_dataset("x_accel",data=x,dtype=np.int16)
        sampleGrp.create_dataset("y_accel",data=y,dtype=np.int16)
        sampleGrp.create_dataset("z_accel",data=z,dtype=np.int16)

        # print progress bar
        progress_points = 50
        progress = int((frame_number)*progress_points/(number_of_frames))
        bar = "".join([u"\u2588"]*progress + [" "]*(progress_points-progress-1))
        print("Progress: %d%%" % ((progress+1)*100/progress_points) + " |" + str(bar) + "| "  ,end="\r") 
    
    print()
    print("Done.\n")

    start_frame =  measurements.get_entries_info(channel_names[1])[0]["id"]
    end_frame =  measurements.get_entries_info(channel_names[1])[-1]["id"]
    number_of_frames = len(measurements.get_entries_info(channel_names[1]))

    print("Extracting Inter-beat interval data:")
    i = 0
    for entry_info in  measurements.get_entries_info(channel_names[1]):

        # extract frame id
        frame_number = i  
        i+=1

        frame_id = entry_info["id"]

        sec = int.from_bytes(measurements.get_entry_data(frame_id)[0:4],"little")
        nanosec = int.from_bytes(measurements.get_entry_data(frame_id)[4:8],"little")
        string_size = int.from_bytes(measurements.get_entry_data(frame_id)[8:16],"little")

        # print("Frame ID " + (measurements.get_entry_data(frame_id)[16:16+string_size]).decode("ascii"))

        # start of message
        start = 16+string_size
        float_size = 8
        inter_beat_interval = struct.unpack("<d",measurements.get_entry_data(frame_id)[start:start+float_size])
        heart_rate = (60*1000/inter_beat_interval[0])
        
        # store data
        sampleGrp = ibeatGrp.create_group("Sample_%s" % (frame_number))
        timeGrp = sampleGrp.create_group("timeStamps")
        timeGrp.create_dataset("nanosec" , data = nanosec, dtype = np.uint32)
        timeGrp.create_dataset("seconds" , data = sec, dtype = np.uint32)
        sampleGrp.create_dataset("heart_rate",data=heart_rate,dtype=np.float64)

        # print progress bar
        progress_points = 50
        progress = int((frame_number)*progress_points/(number_of_frames))
        bar = "".join([u"\u2588"]*progress + [" "]*(progress_points-progress-1))
        print("Progress: %d%%" % ((progress+1)*100/progress_points) + " |" + str(bar) + "| "  ,end="\r") 

    
    print()
    print("Done.\n")


def main():
    convert()
    exit()
    for i in range(7,13):
        convert(i)

if __name__ == "__main__":
    main()