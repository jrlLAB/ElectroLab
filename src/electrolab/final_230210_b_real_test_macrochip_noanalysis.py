import controller
import time

import pypotato as pp
import numpy as np
import matplotlib.pyplot as plt
import softpotato as sp
from scipy.optimize import curve_fit
import os
from scipy.stats import linregress
import shutil
import serial
import time
import dill
from pathlib import Path
from dotenv import load_dotenv

####define com ports for controller and MUX + baudrate (keep at 115200 for both)
controllerPort = 'COM5'
muxPort = 'COM8'
baud_rate = 115200
###setup mux
mux = serial.Serial(port=muxPort, baudrate=baud_rate, timeout=0.1)
###setup controller
setup = controller.Setup(controllerPort, baud_rate)
setup.connect()

#### This section of the code just cycles a couple of states in the multiplexer, it can be deleted (but may cause issues if not present)
mux.write(bytes(str(1), 'utf-8'))
msg = mux.readline()
print(msg.decode('utf-8'))
time.sleep(5)
mux.write(bytes(str(3), 'utf-8'))
msg = mux.readline()
print(msg.decode('utf-8'))
time.sleep(5)
mux.write(bytes(str(5), 'utf-8'))
msg = mux.readline()
print(msg.decode('utf-8'))
time.sleep(5)

wait = 10
move = controller.Motor()
power = controller.MainPower()

# Parameters related to peristaltic pumps
p1_default = [19.801938114061617,0.964367848880719,1.167139063529185e-05,-2.873709837738213e-09]
p2_default = [11.765533598083050, 0.994151183002726, -2.200584843815698e-05, 5.268389857671134e-09]
p_linear = [0,1,0,0]

# Parameters related to liquid volumes & concentrations
conc_tag = np.array([25, 50, 75, 100]) 

# total volume = 1.0 mL (total volume = ratio_conc * 1 mL)
ratio_conc = 1
vol_list_1 = [250*ratio_conc, 500*ratio_conc, 750*ratio_conc, 1000*ratio_conc]
vol_list_2 = [750*ratio_conc, 500*ratio_conc, 250*ratio_conc, 0*ratio_conc]

disp1_cutoff = 670
disp2_cutoff = 580

# Main Power ON
print('\n----MAIN POWER ON----')
power.state('ON')
time.sleep(2)

# Homming
print('\n----NOZZLES HOMING----')
message_home2 = bytes('<homeDisp,0,0>', 'UTF-8')
move.send(message_home2)
time.sleep(wait+15)

print('\n----GANTRY HOMING----')
message_home1 = bytes('<homeGantry,0,0>', 'UTF-8')
move.send(message_home1)
time.sleep(wait+5)

### Nozzle 1 contains redoxmer !!
# p1_default, p2_default, p_linear


### Loop starts (set of concentrations / with cut-off volumes)

###concentration values in 4 element list
conc_used = [0.25e-6,0.5e-6,0.75e-6,1e-6]
conc_str = ['250_uM','500_uM','750_uM','1_mM']

###setup serial commands for the macro electrode chip
serialNum = [11,12,13,14,15,16,17,18]

for iii in range(len(vol_list_1)):

    # Move to the dummy cell
    print('\n----Moving to cell 4 (dummy)----')
    pos = controller.Position_in_cell(4)
    pos.run()
    time.sleep(wait+5)

    print('\n----Dispense in cell 4 (dummy) from Nozzle 1 & 2----')
    dispense_1d = controller.Dispense(nozzle=1, volume=500, wait_time=[0,3,12,3,0], motor_values=[-39000,80,-8530,80,39000], p = p_linear)
    dispense_1d.run()
    time.sleep(7)

    dispense_2d = controller.Dispense(nozzle=2, volume=500, wait_time=[0,3,12,3,0], motor_values=[-39000,80,-9300,80,39000], p = p_linear)
    dispense_2d.run()
    time.sleep(7)

    # Move to the cell
    print('\n----Moving to cell 2----')
    pos = controller.Position_in_cell(2)
    pos.run()
    time.sleep(15)

    ### (0) CHANGE VOLUMES !!!!
    print('\n----Dispense in cell 2 from Nozzle 1 & 2----')

    x = vol_list_1[iii]
    y = vol_list_2[iii]

    if x < disp1_cutoff:
        dispense_1d = controller.Dispense(nozzle=1, volume=x, wait_time=[0,3,12,3,0], motor_values=[-39000,80,-8530,80,39000], p = p1_default)
        print(f'From nozzle 1, dispensing \033[31m{x} \033[0muL  \n')
        dispense_1d.run()
        time.sleep(wait)
    else:
        dispense_1d = controller.Dispense(nozzle=1, volume=x, wait_time=[0,3,12,3,0], motor_values=[-39000,80,-8530,80,39000], p = p_linear)
        print(f'From nozzle 1, dispensing \033[33m{x} \033[0muL  \n')
        dispense_1d.run()
        time.sleep(wait)

    if y < disp2_cutoff:
        dispense_2d = controller.Dispense(nozzle=2, volume=y, wait_time=[0,3,12,3,0], motor_values=[-39000,80,-9230,80,39000], p = p2_default)
        print(f'From nozzle 2, dispensing \033[31m{y} \033[0muL  \n')
        dispense_2d.run()
        time.sleep(wait)
    else:
        dispense_2d = controller.Dispense(nozzle=2, volume=y, wait_time=[0,3,12,3,0], motor_values=[-39000,80,-9230,80,39000], p = p_linear)
        print(f'From nozzle 2, dispensing \033[33m{y} \033[0muL  \n')
        dispense_2d.run()
        time.sleep(wait)

    print(f'Redox + Electrolyte \033[33m{x} \033[0muL and Electrolyte \033[33m{y} \033[0muL has been dispensed \n')

    ##### (1) N2 bubbling - nozzle 2 (10 loops for 3 minutes)
    print('\n----\033[31mN2 bubbling\033[0m----')
    n2_bubbling = controller.N2(loop = 5, nozzle = 2, wait_time = [12,3,12], mode = 'dual')
    n2_bubbling.run()
    time.sleep(7)

    # Main Power OFF (run or skip)
    print('\n----MAIN POWER OFF----')
    power.state('OFF')
    time.sleep(7)


    time.sleep(30)


    
    ##### E-CHEM PART


    ################ Directory Setup ####################

    directory = "Test1_FcMeOH_Macros_" + conc_str[iii]

    ######################### EXPERIMENT INFO ########################
    expInfo = "variable FcMeOH, 100 mM KNO3, Macros, 2/22, 200 um" + directory
    ##################################################################

    # Parent Directory path
    parent_dir = "C:/Users/oliverrz/Desktop/ElectroLab/data/2023_02_22"
    # Path
    path = os.path.join(parent_dir, directory)
    os.mkdir(path)
    print("Directory '% s' created" % directory)
    folder = str(path)
    #####################################################



    ##### Setup
    # Select the potentiostat model to use:
    # emstatpico, chi1205b, chi760e
    #### Potentiostat setup #####
    model = 'chi760e'			 # Model to use
    path_exe = 'C:/Users/oliverrz/Desktop/CHI/chi760e/chi760e.exe'	 # Path to the chi760e.exe
    pp.potentiostat.Setup(model, path_exe, folder)	 # Setup



    ##### Experimental parameters:
    Eini = -0.3     # V, initial potential
    Ev1 = 0.3       # V, first vertex potential
    Ev2 = -0.3      # V, second vertex potential
    Efin = -0.3     # V, final potential
    dE = 0.001      # V, potential increment
    nSweeps = 2     # number of sweeps
    sens = 1e-7     # A/V, current sensitivity                              ### (2) CHANGE THIS !!!!
    header = 'CV'   # header for data file


    ##### Experiment:
    sr = np.array([0.025, 0.05, 0.075, 0.1])          # V/s, scan rate
    # [0.02, 0.04, 0.06, 0.08, 0.1, 0.12, 0.14, 0.16, 0.18, 0.2]
    nsr = sr.size
    i = []
    for y in serialNum:
        mux.write(bytes(str(y), 'utf-8'))
        msg = mux.readline()
        print(msg.decode('utf-8'))
        time.sleep(5)

        for x in range(nsr):
            # initialize experiment:
            fileName = 'Electrode'+ str(y-10) + '_CV_' + str(int(sr[x]*1000)) + 'mVs' + '_'+ conc_str[iii] # base file name for data file
            cv = pp.potentiostat.CV(Eini, Ev1,Ev2, Efin, sr[x], dE, nSweeps, sens, fileName, header)
            # Run experiment:
            cv.run()
            data = pp.load_data.CV(fileName + '.txt', folder, model)
            # load data to do the data analysis later







    # Main Power ON
    print('\n----MAIN POWER ON----')
    power.state('ON')
    time.sleep(5)

    ##### (2) Initial Electrode Rinsing
    ## move_down / <<<LOOP start = suc / flush / equil_flush / suc = LOOP end>>> / move_up

    rinse = controller.Rinse(loop=3, wait_time=[16,13,2,5,12,16]) # change the number of loops
    rinse.run()
    time.sleep(7)


    ##### (3) Electrode strong rinsing with bubbling
    # (SR1) filling reservoir with water
    rinse3 = controller.Rinse(loop=1, wait_time=[16,0,1,5,0,16]) # change the number of loops
    rinse3.run()
    time.sleep(7)

    # Dummy dispensing (SHOULD BE DONE between rinsing & N2 bubbling, owing to error)
    #dispense_2 = controller.Dispense(nozzle=2, volume=10, wait_time=[0,3,12,3,0], motor_values=[-39000,80,-8530,80,39000], p = p_linear)
    #dispense_2.run()
    #time.sleep(wait)

    # (SR2) N2 bubbling - nozzle 2
    print('\n----\033[31mN2 bubbling\033[0m----')
    n2_bubbling = controller.N2(loop = 5, nozzle = 2, wait_time = [12,3,12], mode = 'dual')
    n2_bubbling.run()
    time.sleep(7)

    # (SR3) Suction only
    rinse2 = controller.Rinse(loop=1, wait_time=[16,12,0,5,0,16]) # suction only
    rinse2.run()
    time.sleep(7)

    # (CAN BE DONE without dispensing...)

    # (SR4) N2 drying - nozzle 1 (20 loops for drying at medium flow)
    print('\n----\033[31mN2 drying\033[0m----')
    n2_drying = controller.N2(loop = 7, nozzle = 1, wait_time = [12,3,12], mode = 'single')
    n2_drying.run()
    time.sleep(10)






# Main Power OFF (run or skip)
print('\n----MAIN POWER OFF----')
power.state('OFF')
time.sleep(10)

print('Finished')
setup.disconnect()

### <POWER,1,0>
### <PUMP1,1000,45000>
### <PUMP2,1000,45000>