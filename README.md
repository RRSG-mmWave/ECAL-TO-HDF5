<p float="left">
  <img src="docs/resources/ARU_logo_rectangle.png" width="600" />
  <img src="docs/resources/rrsglogo.png" width="150" /> 
</p>

# ECAL-TO-HDF5

## Author
Nicholas Bowden - UCT MSc

## Dependencies
# Python3.8
This repository was tested on python 3.8

# H5PY
Python Library for reading from and writing to HDF5 files.
```
pip install h5py
```

# Numpy
Python's standard computation library.
```
pip install numpy
```

# OpenCV
Python's main computer vision library.
```
pip install opencv-python
```

## Description
This is a repository to convert data stored in the ecal hdf5 layout to a custom hdf5 layout.\
Current devices supported are:

1. Realsense Depth - Image
2. Realsense Colour - Image
3. Flir Boson Thermal - Image
4. Texas Instruments AWR1843BOOST FMCW Radar - Raw ADC IQ Data
5. Livox Avia LiDAR - PCD
6. Wildstronics Audio - Wave
7. DVExplorer Event Camera - Image and Event Array
8. Ximea Highspeed RGB Camera - Image


However, this code is easy to change to suit any needs required.\
Everything in Ecal-HDF5 is stored in a byte array.\
Just look at the ROS2 message type associated with the ecal measurement channel you wish to convert.\
Ints and Floats have set sizes defined by the message such uint32 or float64.\
Strings and arrays have 8 bytes (uint64) before the data which store the size of associated array.\
The code in the python scripts should show clear examples about how to use the above information to extract the data.

For the radar, please check the [DCA1000-ROS2](https://github.com/RRSG-mmWave/DCA1000-ROS2/tree/m2s2) repo as the radar uses a custom ROS2
message format. 

## Windows Installation
### Install Ecal
Go to: [ecal download](https://eclipse-ecal.github.io/ecal/_download_archive/download_archive_ecal_5_11_4.html#download-archive-ecal-v5-11-4)\
Download and run the executable to install ecal. Change the version in the link as requried. 

### Install Python ECAL Integration
Go to: [ecal download](https://eclipse-ecal.github.io/ecal/_download_archive/download_archive_ecal_5_11_4.html#download-archive-ecal-v5-11-4)\
Download and run the python bindings for python3.8 to install ecal python integration. Change the version in the link as requried. 


## Linux Installation
### Install ECAL
Run the following commands to install ecal:
```bash
sudo add-apt-repository ppa:ecal/ecal-latest
sudo apt-get update
sudo apt-get install ecal
```

### Install Python ECAL Integration
Run the following commands to install ecal python integration:
```bash
sudo apt install python3 python3-pip
sudo apt install python3-ecal5
```

## Run Converter
Run master_convert.py. For the script to work as is you should have the following folder structure
within your working directory:
```
├── ecal_data
│   ├── measurement_name
│       ├── doc
│           ├── description.txt
│   ├── measurement_user_name
│       ├── ecal.ini
│       ├── measurement_user_name_1.hdf5
│       ├── measurement_user_name_2.hdf5
│       ├── etc.
│
├── other_data
│   ├── config.json (the radar config file used to record radar data)
│
├── output_data
│   ├── your outputs will be placed here
```

## HDF5 Output
```
Root
├── Comments
│   ├── experiment_setup
│   ├── sensor_list
│
├── Sensors
│   ├── Realsense_Colour
│       ├── Parametres
│           ├── ...
│       ├── Data
│           ├── Image_1
│                ....
│           ├── Image_N
│               ├── image_data
│               ├── Timestamps
│                   ├── seconds
│                   ├── nano_seconds
│
│   ├── Realsense_Depth
│       ├── Parametres
│           ├── ...
│       ├── Data
│           ├── Image_1
│                ....
│           ├── Image_N
│               ├── image_data
│               ├── Timestamps
│                   ├── seconds
│                   ├── nano_seconds
│
│   ├── Ximea_Raw
│       ├── Parametres
│           ├── ...
│       ├── Data
│           ├── Image_1
│                ....
│           ├── Image_N
│               ├── image_data
│               ├── Timestamps
│                   ├── seconds
│                   ├── nano_seconds
│
│   ├── Boson_Thermal
│       ├── Parametres
│           ├── ...
│       ├── Data
│           ├── Image_1
│                ....
│           ├── Image_N
│               ├── image_data
│               ├── Timestamps
│                   ├── seconds
│                   ├── nano_seconds
│
│   ├── Wildtronics_Audio
│       ├── Parametres
│           ├── ...
│       ├── Data
│           ├── Audio_Chunk_1
│                ....
│           ├── Audio_Chunk_N
│               ├── audio_bytes
│               ├── Timestamps
│                   ├── seconds
│                   ├── nano_seconds
│
│   ├── TI_Radar
│       ├── Parametres
│           ├── ...
│       ├── Data
│           ├── Frame_1
│                ....
│           ├── Frame_N
│               ├── frame_data
│               ├── Timestamps
│                   ├── seconds
│                   ├── nano_seconds
│
│   ├── Livox_Lidar
│       ├── Parametres
│           ├── ...
│       ├── Data
│           ├── PCD_1
│                ....
│           ├── PCD_N
│               ├── pcd_header
│               ├── pcd_data
│               ├── Timestamps
│                   ├── seconds
│                   ├── nano_seconds
│
│   ├── DVExplorer_Event
│       ├── Event_Images
│           ├── Parametres
│           ├── ...
│       ├── Data
│           ├── Image_1
│                ....
│           ├── Image_N
│               ├── image_data
│               ├── Timestamps
│                   ├── seconds
│                   ├── nano_seconds
|
│       ├── Event_Arrays
│           ├── Parametres
│           ├── ...
│       ├── Data
│           ├── Array_1
│                ....
│           ├── Array_N
│               ├── events_xy
│               ├── events_seconds
│               ├── events_nano_seconds
│               ├── events_polarity
│               ├── number_of_events
│               ├── Timestamps
│                   ├── seconds
│                   ├── nano_seconds
```
