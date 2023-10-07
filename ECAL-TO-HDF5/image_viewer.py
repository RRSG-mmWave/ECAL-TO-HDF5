import h5py
from matplotlib import pyplot as plt
import os
import numpy as np

# get file
working_dir = os.path.dirname(__file__)
output_folder = "output_data/"
camera_file_to_view = "Livox_PointCloud_Exp3.hdf5"
camera_file = os.path.join(working_dir,output_folder,camera_file_to_view)
f = h5py.File(camera_file, 'r')

print(f["Data"]["PCD_Frame_70"].keys())
explanation_bytes = np.array(f["Params"]["Field_Info_Explanation"])[0].decode("ascii")
print(explanation_bytes)

# print(b"".join(f["Data"]["PCD_Frame_70"]["PCD_Bytes"]))
print(np.array(f["Data"]["PCD_Frame_70"]["timeStamps"]["seconds"]))
print(np.array(f["Data"]["PCD_Frame_70"]["timeStamps"]["nanosec"]))
print(np.array(f["Data"]["PCD_Frame_70"]["timeStamps"]["seconds"])+ 1e-9*np.array(f["Data"]["PCD_Frame_70"]["timeStamps"]["nanosec"]))




exit()
# print(f.keys())
# display an image
image = np.array(f["Data"]["Frame_120"]["frameData"])
print(image.shape)
plt.imshow(image,cmap="Greys_r")
plt.show()