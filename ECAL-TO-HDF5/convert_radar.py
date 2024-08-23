
# processing imports
import numpy as np
import os
import json

import h5py
from ecal.measurement.hdf5 import Meas
import glob

def sort_data(frame_data,nSamples,nChirps,nVChannels,real_or_complex):
    """Sorts raw unsorted (int16) radar data into 3D radar data cube. 
    
    Based off of TI MATLAB code.
    
    input : frame_data  ->  Raw unsorted int16 radar data.
    
    output : data_cube  ->  Is a 3D array with the dimensions [nsamples,nChirps,nChannels]
    """
    # calculate frame data size
    BYTESPERSAMPLE = 2
    total_samples = nSamples*nChirps*nVChannels*real_or_complex
    output_length = int(total_samples/BYTESPERSAMPLE)
    
    # construct complex samples
    data_cube = np.zeros(output_length,dtype=np.complex64)
    data_cube[ ::2] = frame_data[ ::4] + 1j*frame_data[2::4]
    data_cube[1::2] = frame_data[1::4] + 1j*frame_data[3::4]

    # reshape the array
    data_cube = np.reshape(data_cube, (nSamples, nVChannels, nChirps),order='F')
    data_cube = np.transpose(data_cube, (0, 2, 1)) 

    return data_cube
    
def convert(path_to_folder, path_config_json, group_handle,channel_name = "rt/radar_data"):

    print("CONVERTING ECAL RADAR MEASUREMENT TO HDF5:")
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


    # parameter source file
    # sort = True
    # try:
    #     param_file = h5py.File(os.path.join(working_dir,path_to_input,file_dict["PARAM_HDF5"]))
    #     print("Loading parameter hdf5 file.")

    #     # store params in dict
    #     outer_keys = []
    #     dict_per_cmd_list = []
    #     for cmd in (param_file["Params"].keys()):
    #         outer_keys.append(cmd)
    #         inner_keys = []
    #         inner_vals = []
    #         for param in (param_file["Params"][cmd]):
    #             inner_keys.append(param)
    #             inner_vals.append(int(param_file["Params"][cmd][param][()]))
    #         dict_per_cmd_list.append(dict(zip(inner_keys,inner_vals)))
    #     configDict = dict(zip(outer_keys,dict_per_cmd_list))
        
    #     # dump to json
    #     out_file = open("other_data/config.json", "w")
    #     json.dump(configDict, out_file, indent = 6)
    #     out_file.close()

    # except:
    try:
        f = open(os.path.join(working_dir,path_config_json))
        print("Loading parameter json file.")
        configDict = json.load(f)
    except:
        print("No Parameter File Found.")
        exit()

    # Calculate channels,
    recBitMask =  bin(int(np.array(configDict["channelCfg"]["rxChannelEn"])))[2:] # convert number to bit mask string with bin()
    numRx = 0
    for bit in recBitMask:  # count the number of bits = 1 in bit mask to get number of receiver channels enabled
        numRx = numRx + int(bit)
    numTx  = int(np.array(configDict["frameCfg"]["chirpEndIndex"])) - int(np.array(configDict["frameCfg"]["chirpStartIndex"])) + 1
    nVChannels = numTx*numRx

    # get number of chirps and samples
    nChirps  = configDict["frameCfg"]["numChirps"]
    nSamples = configDict["profileCfg"]["numAdcSamples"]

    # get and calculate intermediate params
    real_or_complex  = (configDict["adcbufCfg"]["adcOutputFmt"] + 2) % 3

    for command in configDict:
        commandGrp = paramGrp.create_group(command)
        for parameter in configDict[command]:
            commandGrp.create_dataset(parameter,data=configDict[command][parameter])

    paramGrp.create_dataset("sorted_data",data=True)

    # get start and end frame ids
    number_of_frames = len(measurements.get_entries_info(channel_name))
    print("Frames to convert:", number_of_frames)

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
        frame = sort_data(frame,nSamples,nChirps,nVChannels,real_or_complex)

        # store data
        frameGrp = dataGrp.create_group("Frame_%s" % (frame_number))
        timeGrp = frameGrp.create_group("Timestamps")
        timeGrp.create_dataset("nano_seconds" , data = nanosec, dtype = np.uint32)
        timeGrp.create_dataset("seconds" , data = sec, dtype = np.uint32)
        frameGrp.create_dataset("frame_data",data=frame,dtype=np.complex64)

        # print progress bar
        progress_points = 50
        progress = int((frame_number)*progress_points/(number_of_frames))
        bar = "".join([u"\u2588"]*progress + [" "]*(progress_points-progress-1))
        print("Progress: %d%%" % ((progress+1)*100/progress_points) + " |" + str(bar) + "| "  ,end="\r") 
    
    print("\n\n")
