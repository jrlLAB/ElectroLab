import controller
import time
from hardpotato import *
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

import datetime

number_runs = 5

start_time = time.time()

###make parent folder
experiment_name = "expt1"
parent_dir1 = "C:/Data Path"
# Path
path = os.path.join(parent_dir1, experiment_name)
os.mkdir(path)
print("Directory '% s' created" % experiment_name)
parent_folder = str(path)
######################### GENERATE DUPLICATE CODE ################
# generate filename with timestring
copied_script_name = time.strftime("%Y-%m-%d_%H%M") + "_" + os.path.basename(__file__)
# copy script
shutil.copy(__file__, parent_folder + os.sep + copied_script_name)
##################################################################


############################ setup control board and MUX###############################

####define com ports for controller and MUX + baudrate (keep at 115200 for both)
controllerPort = "COM5"
muxPort = "COM4"
baud_rate = 115200
###setup mux
mux = serial.Serial(port=muxPort, baudrate=baud_rate, timeout=0.1)
###setup controller
setup = controller.Setup(controllerPort, baud_rate)
setup.connect()

#### This section of the code just cycles a couple of states in the multiplexer, it can be deleted (but may cause issues if not present)
mux.write(bytes(str(1), "utf-8"))
msg = mux.readline()
print(msg.decode("utf-8"))
time.sleep(5)
mux.write(bytes(str(3), "utf-8"))
msg = mux.readline()
print(msg.decode("utf-8"))
time.sleep(5)
mux.write(bytes(str(5), "utf-8"))
msg = mux.readline()
print(msg.decode("utf-8"))
time.sleep(5)

###setup serial commands for the macro electrode chip
serialNum = [11, 12, 13, 14, 15, 16, 17, 18]

##########setup pstat ##################3
##### Setup
# Select the potentiostat model to use:
# emstatpico, chi1205b, chi760e
#### Potentiostat setup #####
model = "chi760e"  # Model to use
path_exe = (
    "C:/Potentiostat Path/chi760e.exe"  # Path to the chi760e.exe
)
potentiostat.Setup(model, path_exe, parent_folder)  # Setup

#################### Fluidics parameters ###########################
wait = 10
move = controller.Motor()
power = controller.MainPower()

# Parameters related to peristaltic pumps
p1_new = [
    13.712609063042798,
    0.977763871750637,
    4.104248850640944e-05,
    -4.143399187088928e-08,
]
p1_default = [
    19.801938114061617,
    0.964367848880719,
    1.167139063529185e-05,
    -2.873709837738213e-09,
]
p2_default = [
    11.765533598083050,
    0.994151183002726,
    -2.200584843815698e-05,
    5.268389857671134e-09,
]
p_linear = [0, 1, 0, 0]

disp1_cutoff = 600
disp2_cutoff = 600


########### start of script! #################################################

# Main Power ON
print("\n----MAIN POWER ON----")
power.state("ON")
time.sleep(2)

# Homming
print("\n----NOZZLES HOMING----")
message_home2 = bytes("<homeDisp,0,0>", "UTF-8")
move.send(message_home2)
time.sleep(wait + 15)

print("\n----GANTRY HOMING----")
message_home1 = bytes("<homeGantry,0,0>", "UTF-8")
move.send(message_home1)
time.sleep(wait + 5)


######## Dispense in the dummy cell  + cleaning ######################################################
# Move to the dummy cell
print("\n----Moving to cell 4 (dummy)----")
pos = controller.Position_in_cell(4)
pos.run()
time.sleep(wait + 5)

# Dummy dispensing to remove trapped air bubbles in tubes
print("\n----Dispense in cell 4 (dummy) from Nozzle 1 & 2----")
dispense_1d = controller.Dispense(
    nozzle=1,
    volume=200,
    speed=8000,
    wait_time=[0, 3, 26.4, 3, 0],
    motor_values=[-9000, 20, -2755, 20, 9000],
    p=p_linear,
)
dispense_1d.run()
time.sleep(7)

dispense_2d = controller.Dispense(
    nozzle=2,
    volume=200,
    speed=8000,
    wait_time=[0, 3, 26.4, 3, 0],
    motor_values=[-9000, 20, -2755, 20, 9000],
    p=p_linear,
)
dispense_2d.run()
time.sleep(7)

# Dummy cell suction
suction_only = controller.Rinse_dummy(loop=1, wait_time=[16, 12, 0, 0, 16])
suction_only.run()
time.sleep(5)


######## Move to actual cell  ##########################################################

# Move to the cell
print("\n----Moving to cell 3----")
pos = controller.Position_in_cell(3)
pos.run()
time.sleep(15)

for a in range(number_runs):
    ### dispense 1 mL of Electrolyte first ##############################################
    dispense_2d = controller.Dispense(
        nozzle=2,
        volume=1000,
        speed=8000,
        wait_time=[0, 3, 26.4, 3, 0],
        motor_values=[-9000, 20, -2755, 20, 9000],
        p=p_linear,
    )
    print(f"From nozzle 2, dispensing \033[33m{1000} \033[0muL  \n")
    dispense_2d.run()
    time.sleep(wait)

    ### Argon bubbling #################################################################
    print("\n----\033[31mN2 bubbling\033[0m----")
    n2_bubbling = controller.N2(loop=1, nozzle=2, wait_time=[12, 3, 12], mode="dual")
    n2_bubbling.run()
    time.sleep(7)

    ### Main Power OFF #################################################################
    print("\n----MAIN POWER OFF----")
    power.state("OFF")
    time.sleep(15)

    ########### echem with just electrolyte ######################################################
    ##### Experimental parameters:
    Ei = -0.2  # V, initial potential
    Eh = 0.3  # V, first vertex potential
    El = -0.2  # V, second vertex potential
    nSweeps = 2  # number of sweeps
    sens = 1e-7  # A/V, current sensitivity                              ### CHANGE THIS IF NEEDED
    header = "CV"  # header for data file
    ##### Experiment:
    sr = np.array([0.1, 0.15, 0.2, 0.25, 0.3])  # V/s, scan rate
    for y in serialNum:
        mux.write(bytes(str(y), "utf-8"))
        msg = mux.readline()
        print(msg.decode("utf-8"))
        time.sleep(5)
        for x in range(sr.size):
            # initialize experiment:
            fileName_CV = f"0mM_Electrode{y-10}_{int(sr[x]*1000)}mVs_CV_{a+1}"  # base file name for data file
            cv = potentiostat.CV(
                Eini=Ei,
                Ev1=Eh,
                Ev2=El,
                Efin=Ei,
                sr=sr[x],
                sens=sens,
                dE=0.001,
                nSweeps=2,
                qt=2,
                fileName=fileName_CV,
            )
            # Run experiment:
            cv.run()
            data = load_data.CV(fileName_CV + ".txt", parent_folder, model)
            # load data to do the data analysis later

    ####################################### cleaning ##############################################
    ### Main Power ON #############################################################################
    print("\n----MAIN POWER ON----")
    power.state("ON")
    time.sleep(5)

    ### Initial Electrode Rinsing #################################################################
    ## "wait_time" in Rinse function (0 will skip the step, and below is the sequence)
    ## (1) Down / [LOOP start [ (2) suction / (3) flush / (4) suction] LOOP end] / (5) Up
    ## = [16, 12, 15, 12, 16]
    rinse = controller.Rinse(
        loop=3, wait_time=[16, 12, 15, 12, 16]
    )  # change the number of loops if needed
    rinse.run()
    time.sleep(5)

    ### Electrode strong rinsing / bubbling / drying (SR) ###############################################
    # (SR1) Filling reservoir with solvent
    print("\n----\033[31m Filling reservoir with solvent \033[0m----")
    filling_only = controller.Rinse(loop=1, wait_time=[16, 0, 15, 0, 16])
    filling_only.run()

    # (SR2) Argon bubbling
    print("\n----\033[31mN2 bubbling\033[0m----")
    n2_bubbling = controller.N2(loop=1, nozzle=2, wait_time=[12, 3, 12], mode="dual")
    n2_bubbling.run()
    time.sleep(7)

    # (SR3) Suction only
    suction_only = controller.Rinse(loop=1, wait_time=[16, 12, 0, 0, 16])
    suction_only.run()
    time.sleep(7)

    # (SR4) Argon drying
    print("\n----\033[31mN2 drying\033[0m----")
    n2_drying = controller.N2(loop=1, nozzle=1, wait_time=[12, 3, 12], mode="single")
    n2_drying.run()
    time.sleep(10)

    ### dispense 1 mL of FcMeOh ########################################################################
    dispense_1d = controller.Dispense(
        nozzle=1,
        volume=1000,
        speed=8000,
        wait_time=[0, 3, 26.4, 3, 0],
        motor_values=[-9000, 20, -2755, 20, 9000],
        p=p_linear,
    )
    print(f"From nozzle 1, dispensing \033[33m{1000} \033[0muL  \n")
    dispense_1d.run()
    time.sleep(wait)

    ### Argon bubbling #################################################################################
    print("\n----\033[31mN2 bubbling\033[0m----")
    n2_bubbling = controller.N2(loop=1, nozzle=2, wait_time=[12, 3, 12], mode="dual")
    n2_bubbling.run()
    time.sleep(7)

    ### Main Power OFF ##################################################################################
    print("\n----MAIN POWER OFF----")
    power.state("OFF")
    time.sleep(15)

    ########### echem with fcmeoh #######################################################################
    ##### Experimental parameters:
    Ei = -0.2  # V, initial potential
    Eh = 0.3  # V, first vertex potential
    El = -0.2  # V, second vertex potential
    nSweeps = 2  # number of sweeps
    sens = 1e-7  # A/V, current sensitivity                              ### (2) CHANGE THIS !!!!
    header = "CV"  # header for data file
    ##### Experiment:
    sr = np.array([0.1, 0.15, 0.2, 0.25, 0.3])  # V/s, scan rate
    for y in serialNum:
        mux.write(bytes(str(y), "utf-8"))
        msg = mux.readline()
        print(msg.decode("utf-8"))
        time.sleep(5)
        for x in range(sr.size):
            # initialize experiment:
            fileName_CV = f"1mM_Electrode{y-10}_{int(sr[x]*1000)}mVs_CV_{a+1}"  # base file name for data file
            cv = potentiostat.CV(
                Eini=Ei,
                Ev1=Eh,
                Ev2=El,
                Efin=Ei,
                sr=sr[x],
                sens=sens,
                dE=0.001,
                nSweeps=2,
                qt=2,
                fileName=fileName_CV,
            )
            # Run experiment:
            cv.run()
            data = load_data.CV(fileName_CV + ".txt", parent_folder, model)
            # load data to do the data analysis later

    ####################################### cleaning ##############################################
    # Main Power ON
    print("\n----MAIN POWER ON----")
    power.state("ON")
    time.sleep(5)

    ### Initial Electrode Rinsing #################################################################
    ## "wait_time" in Rinse function (0 will skip the step, and below is the sequence)
    ## (1) Down / [LOOP start [ (2) suction / (3) flush / (4) suction] LOOP end] / (5) Up
    ## = [16, 12, 15, 12, 16]

    rinse = controller.Rinse(
        loop=3, wait_time=[16, 12, 15, 12, 16]
    )  # change the number of loops if needed
    rinse.run()
    time.sleep(5)

    ### Electrode strong rinsing / bubbling / drying (SR) ###############################################
    # (SR1) Filling reservoir with solvent
    print("\n----\033[31m Filling reservoir with solvent \033[0m----")
    filling_only = controller.Rinse(loop=1, wait_time=[16, 0, 15, 0, 16])
    filling_only.run()

    # (SR2) Argon bubbling
    print("\n----\033[31mN2 bubbling\033[0m----")
    n2_bubbling = controller.N2(loop=1, nozzle=2, wait_time=[12, 3, 12], mode="dual")
    n2_bubbling.run()
    time.sleep(7)

    # (SR3) Suction only
    suction_only = controller.Rinse(loop=1, wait_time=[16, 12, 0, 0, 16])
    suction_only.run()
    time.sleep(7)

    # (SR4) Argon drying
    print("\n----\033[31mN2 drying\033[0m----")
    n2_drying = controller.N2(loop=1, nozzle=1, wait_time=[12, 3, 12], mode="single")
    n2_drying.run()
    time.sleep(10)

########## Main Power OFF ##################################################################################
print("\n----MAIN POWER OFF----")
power.state("OFF")
time.sleep(10)

print("Finished")
setup.disconnect()

print("\n----\033[31m Print the total time duration \033[0m----")
end_time = time.time()
total_time = end_time - start_time
total_time_list = str(datetime.timedelta(seconds=total_time)).split(".")
print(total_time_list[0])  # Hrs:Mins:Secs format
