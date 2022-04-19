# Hardware AI
<br/>

## mpu6050_demo
Arduino code used for the Bluno with the IMU.
<br/> <br/>

## network_hardware
top.cpp and top.h are for Vivado HLS. top.h contains the hardcode weights. Will have to populate with new weights from NN training.ipynb when a new model is trained.  Also contains XSA files containing .bit and .hwh which are exported from Vivado. 
<br/> <br/>
Bitstream contains duplicated pairs of AXI DMA + HLS Coprocessor, one for each player. 

<br/> <br/>
## network_software_deployment
Software deployment of neural network. 


<br/> <br/>
## network_training
Files used for the training of neural network. Trained in a conda environment similar to the one in **network_software_deployment**. Contains CSV files which were logged using serial_data_logging.py with the Bluno + IMU connected. 
<br/> <br/>
NN training.ipynb requires exactly 100 values for each sample/gesture, hence the python file for filtering.



