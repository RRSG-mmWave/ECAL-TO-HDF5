
# processing imports
import numpy as np
import os
import json

import h5py
from ecal.measurement.hdf5 import Meas
import glob
    
def convert(expNum=3, path_to_input="",filename="Radar_Data"):

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

    file_dict = {"PARAM_HDF5" : "other_data/params.hdf5",
                 "PARAM_JSON" : "other_data/config.json",
                 "NOTES_EXPR" : base_dir+"doc/description.txt",
                 "ECAL_DATA"  : base_dir+"m2s2-NUC13ANKi7/"}

    try:
        os.mkdir(os.path.join(working_dir,"output_data/"))
    except:
        pass

    ## Load source files
    print("LOAD SOURCE FILES:")
    working_dir = os.path.dirname(__file__)

    # parameter source file
    # sort = True
    try:
        param_file = h5py.File(os.path.join(working_dir,path_to_input,file_dict["PARAM_HDF5"]))
        print("Loading parameter hdf5 file.")

        # store params in dict
        outer_keys = []
        dict_per_cmd_list = []
        for cmd in (param_file["Params"].keys()):
            outer_keys.append(cmd)
            inner_keys = []
            inner_vals = []
            for param in (param_file["Params"][cmd]):
                inner_keys.append(param)
                inner_vals.append(int(param_file["Params"][cmd][param][()]))
            dict_per_cmd_list.append(dict(zip(inner_keys,inner_vals)))
        configDict = dict(zip(outer_keys,dict_per_cmd_list))
        
        # dump to json
        out_file = open("other_data/config.json", "w")
        json.dump(configDict, out_file, indent = 6)
        out_file.close()

    except:
        try:
            f = open(os.path.join(working_dir,file_dict["PARAM_JSON"]))
            print("Loading parameter json file.")
            configDict = json.load(f)
        except:
            print("No Parameter File Found.")
            exit()

    # notes source 
    print("Loading experiment notes file.")
    with open(os.path.join(working_dir,path_to_input,file_dict["NOTES_EXPR"]), 'r') as file:
        data = file.read()     

    # data source 
    print("Loading data files.\n")
    ecal_folder = os.path.join(working_dir,path_to_input,file_dict["ECAL_DATA"])
    print(ecal_folder)
    
    # create 
    print("CREATING OUTPUT FILE:")
    try:
        out_file = h5py.File(os.path.join(working_dir,"output_data/%s"%(filename)),'x')
    except:
        print("An output file of that name already exists.\n")

    # create starting hierarchy
    print("Storing config data.\n")
    dataGrp = out_file.create_group("Data")
    paramGrp = out_file.create_group("Params")

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
    commentGrp = out_file.create_group("Comments")
    radar=["AWR1843BOOST".encode("ascii")]
    radarTypeDSet = commentGrp.create_dataset("radar_type", shape=(len(radar),1), data=radar)    
    setup=[data.encode("ascii")]  
    setupCommentsDSet = commentGrp.create_dataset("experiment_setup", shape=(len(setup),1), data=setup) 

    ## Start Conversion 
    # Create a measurement (pass either a .hdf5 file or a measurement folder)
    print("CONVERTING:")
    measurements = Meas(ecal_folder)

    # Retrieve the channels in the measurement by calling measurement.channel_names
    # channel_name_index = -1
    # channel_name = measurements.get_channel_names()[channel_name_index]
    # print(channel_name)
    channel_name = "rt/radar/raw_data"
    
    # get start and end frame ids
    # start_frame =  measurements.get_entries_info(channel_name)[0]["id"]
    # end_frame =  measurements.get_entries_info(channel_name)[-1]["id"]
    number_of_frames = len(measurements.get_entries_info(channel_name))
    print(number_of_frames)

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
        secsDs = timeGrp.create_dataset("seconds" , data = sec, dtype = np.uint32)
        frameGrp.create_dataset("frameData",data=frame,dtype=np.int16)

        # print progress bar
        progress_points = 50
        progress = int((frame_number)*progress_points/(number_of_frames))
        bar = "".join([u"\u2588"]*progress + [" "]*(progress_points-progress-1))
        print("Progress: %d%%" % ((progress+1)*100/progress_points) + " |" + str(bar) + "| "  ,end="\r") 
    
    print()

def main():
    # convert()
    # exit()
    for i in range(3,8):
        convert(i)

if __name__ == "__main__":
    main()