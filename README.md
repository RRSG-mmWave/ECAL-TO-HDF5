<p float="left">
  <img src="docs/resources/ARU_logo_rectangle.png" width="600" />
  <img src="docs/resources/rrsglogo.png" width="150" /> 
</p>

# ECAL-TO-HDF5

## Author
Nicholas Bowden - UCT MSc

## Dependencies
#### Python3.8
This repository was tested on python 3.8

#### H5PY
Python Library for reading from and writing to HDF5 files.
```
pip install h5py
```

#### Numpy
Python's standard computation library.
```
pip install numpy
```

#### OpenCV
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
9. Polar H10 - IMU and Heart rate


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

### Notes
If you want separate files per data-set you can just enable one sensor at a time in the mapping.    
The radar config and parameters must be provided as a json called config.json of the correct format in folder other_data.   
The only parts of the master convert that need to be changed are at the top of the main function:
```python 
    
    # Specify data path and output names
    base_dir = "ecal_data" # the folder with your ecal data
    measurement_name = "Exp 3"
    host_username = "m2s2-NUC13ANKi7/" # it found as a sub dir of ecal meas folder 
    filename = "m2s2_cheetah_run3.hdf5"
    
    # use this map to enable sensors 
    sensor_list = {
        "Realsense_Colour"  :   False,
        "Realsense_Depth"   :   False,
        "Ximea_Raw"         :   False,
        "Boson_Thermal"     :   False,
        "Wildtronics_Audio" :   False,
        "TI_Radar"          :   True,
        "Livox_Lidar"       :   False,
        "DVExplorer_Event"  :   False
    }

    # Only thing that might need to be changed after this point is channel name used 
    # which is an argument to each convert function. Check default against channels 
    # listed in terminal when this script is run.

```
