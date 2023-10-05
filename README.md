<p float="left">
  <img src="docs/resources/ARU_logo_rectangle.png" width="600" />
  <img src="docs/resources/rrsglogo.png" width="150" /> 
</p>

# ECAL-TO-HDF5

## Author
Nicholas Bowden - UCT MSc

## Description
This is a repository to convert data stored in the ecal hdf5 layout to a custom hdf5 layout.\
Current devices supported are:

1. Realsense Depth - Image
2. Realsense Infra - Image
2. Realsense Colour - Image
3. Flir Boson Thermal - Image
4. Texas Instruments AWR1843BOOST FMCW Radar - Raw ADC IQ Data

However, this code is easy to change to suit any needs required.\
Everything in Ecal-HDF5 is stored in a byte array.\
Just look at the ROS2 message type associated with the ecal measurement channel you wish to convert.\
Ints and Floats have set sizes defined by the message such uint32 or float64.\
Strings and arrays have 8 bytes before the data which store the size of associated array.\
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

