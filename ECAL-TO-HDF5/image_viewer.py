import h5py
from matplotlib import pyplot as plt
import os
import numpy as np

# get file
working_dir = os.path.dirname(__file__)
output_folder = "output_data/"
camera_file_to_view = "m2s2_cheetah_run3.hdf5"
camera_file = os.path.join(working_dir,output_folder,camera_file_to_view)
f = h5py.File(camera_file, 'r')

print(np.array(f["Comments"]["sensor_list"]))
print(f["Sensors"]["DVExplorer_Event"]["Event_Arrays"]["Data"]["Event_Array_208"].keys())
event_array = f["Sensors"]["DVExplorer_Event"]["Event_Arrays"]["Data"]["Event_Array_208"]
event_array_seconds = event_array["event_list_seconds"][45]
event_array_nano_seconds = event_array["event_list_nano_seconds"][45]
print(event_array_seconds + 1e-9*event_array_nano_seconds)


event_array_time = f["Sensors"]["DVExplorer_Event"]["Event_Arrays"]["Data"]["Event_Array_208"]["Timestamps"]
event_array_seconds = np.array(event_array_time["seconds"])
event_array_nano_seconds = np.array(event_array_time["nano_seconds"])
print(event_array_seconds + 1e-9*event_array_nano_seconds)



exit()
print(f["Sensors"]["Livox_Lidar"]["Data"]["PCD_1"].keys())
header = np.array(f["Sensors"]["Livox_Lidar"]["Data"]["PCD_1"]["pcd_header"])[0].decode("ascii")
print(header)

data = np.array(f["Sensors"]["Livox_Lidar"]["Data"]["PCD_1"]["pcd_data"][0:100])
print(data)

# print(b"".join(f["Data"]["PCD_Frame_70"]["PCD_Bytes"]))
# print(np.array(f["Data"]["PCD_Frame_70"]["timeStamps"]["seconds"]))
# print(np.array(f["Data"]["PCD_Frame_70"]["timeStamps"]["nanosec"]))
print(np.array(f["Sensors"]["Livox_Lidar"]["Data"]["PCD_1"]["Timestamps"]["seconds"])+ 1e-9*np.array(f["Sensors"]["Livox_Lidar"]["Data"]["PCD_1"]["Timestamps"]["nano_seconds"]))




exit()
# print(f["Sensors"]["Realsense_Colour"]["Data"]["Image_1"])

# display an image
image = np.array(f["Sensors"]["Boson_Thermal"]["Data"]["Image_1"]["image_data"])
print(image.shape)
plt.imshow(image,cmap="Greys_r")
plt.show()