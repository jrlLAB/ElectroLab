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
controllerPort = "COM5"
muxPort = "COM11"
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

# Parameters related to liquid volumes & concentrations
conc_tag = np.array([0, 25, 50, 75, 100])

# total volume = 1.0 mL (total volume = ratio_conc * 1 mL)
ratio_conc = 1
vol_list_1 = [
    0 * ratio_conc,
    250 * ratio_conc,
    500 * ratio_conc,
    750 * ratio_conc,
    1000 * ratio_conc,
]
vol_list_2 = [
    1000 * ratio_conc,
    750 * ratio_conc,
    500 * ratio_conc,
    250 * ratio_conc,
    0 * ratio_conc,
]

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

### Dispenser 1 (redoxmer + electrolyte)
### Dispenser 2 (electrolyte)

###concentration values in 4 element list
conc_used = [0e-6, 0.25e-6, 0.5e-6, 0.75e-6, 1e-6]
conc_str = ["0_uM", "250_uM", "500_uM", "750_uM", "1_mM"]

###setup serial commands for the macro electrode chip
serialNum = [11, 12, 13, 14, 15, 16, 17, 18]

for iii in range(len(vol_list_1)):
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
        wait_time=[0, 3, 12, 3, 0],
        motor_values=[-39000, 80, -9300, 80, 39000],
        p=p_linear,
    )
    dispense_2d.run()
    time.sleep(7)

    ######## Move to actual cell  ##########################################################

    print("\n----Moving to cell 2----")
    pos = controller.Position_in_cell(2)
    pos.run()
    time.sleep(15)

    ### dispense solutions in the cell ##############################################
    print("\n----Dispense in cell 2 from Nozzle 1 & 2----")

    x = vol_list_1[iii]
    y = vol_list_2[iii]

    if x == 0:
        pass
    elif x < disp1_cutoff:
        dispense_1d = controller.Dispense(
            nozzle=1,
            volume=x,
            speed=8000,
            wait_time=[0, 3, 26.4, 3, 0],
            motor_values=[-9000, 20, -2755, 20, 9000],
            p=p1_new,
        )
        print(f"From nozzle 1, dispensing \033[31m{x} \033[0muL  \n")
        dispense_1d.run()
        time.sleep(wait)
    else:
        dispense_1d = controller.Dispense(
            nozzle=1,
            volume=x,
            speed=8000,
            wait_time=[0, 3, 26.4, 3, 0],
            motor_values=[-9000, 20, -2755, 20, 9000],
            p=p_linear,
        )
        print(f"From nozzle 1, dispensing \033[33m{x} \033[0muL  \n")
        dispense_1d.run()
        time.sleep(wait)

    if y == 0:
        pass
    elif y < disp2_cutoff:
        dispense_2d = controller.Dispense(
            nozzle=2,
            volume=y,
            wait_time=[0, 3, 12, 3, 0],
            motor_values=[-39000, 80, -9230, 80, 39000],
            p=p2_default,
        )
        print(f"From nozzle 2, dispensing \033[31m{y} \033[0muL  \n")
        dispense_2d.run()
        time.sleep(wait)
    else:
        dispense_2d = controller.Dispense(
            nozzle=2,
            volume=y,
            wait_time=[0, 3, 12, 3, 0],
            motor_values=[-39000, 80, -9230, 80, 39000],
            p=p_linear,
        )
        print(f"From nozzle 2, dispensing \033[33m{y} \033[0muL  \n")
        dispense_2d.run()
        time.sleep(wait)

    print(
        f"Redox + Electrolyte \033[33m{x} \033[0muL and Electrolyte \033[33m{y} \033[0muL has been dispensed \n"
    )

    ### Argon short bubbling (to avoid excessive evaporation)##########
    print("\n----\033[31mN2 bubbling\033[0m----")
    n2_bubbling = controller.N2(loop=1, nozzle=2, wait_time=[12, 3, 12], mode="dual")
    n2_bubbling.run()
    time.sleep(7)

    ### Main Power OFF #################################################################
    print("\n----MAIN POWER OFF----")
    power.state("OFF")
    time.sleep(7)

    time.sleep(30)

    ############# E-CHEM PART ###############################################

    ################ Directory Setup ####################

    directory = "FcMeOH_Macros_" + conc_str[iii]

    ######################### EXPERIMENT INFO ########################
    expInfo = (
        "variable conc, FRESH 1mM FcMeOH, 100 mM KNO3, Macros"
        + directory
    )
    ##################################################################

    # Parent Directory path
    parent_dir = "C:/Data Path"
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
    model = "chi760e"  # Model to use
    path_exe = (
        "C:/Potentiostat Path/chi760e.exe"  # Path to the chi760e.exe
    )
    pp.potentiostat.Setup(model, path_exe, folder)  # Setup

    ##### Experimental parameters:
    Eini = -0.2  # V, initial potential
    Ev1 = 0.3  # V, first vertex potential
    Ev2 = -0.2  # V, second vertex potential
    Efin = -0.2  # V, final potential
    dE = 0.001  # V, potential increment
    nSweeps = 2  # number of sweeps
    sens = 1e-7  # A/V, current sensitivity                              ### (2) CHANGE THIS !!!!
    header = "CV"  # header for data file

    ##### Experiment:
    sr = np.array([0.05, 0.1, 0.15, 0.2, 0.25])  # V/s, scan rate
    # [0.02, 0.04, 0.06, 0.08, 0.1, 0.12, 0.14, 0.16, 0.18, 0.2]
    nsr = sr.size
    i = []
    for y in serialNum:
        mux.write(bytes(str(y), "utf-8"))
        msg = mux.readline()
        print(msg.decode("utf-8"))
        time.sleep(5)

        for x in range(nsr):
            # initialize experiment:
            fileName = (
                "Electrode"
                + str(y - 10)
                + "_CV_"
                + str(int(sr[x] * 1000))
                + "mVs"
                + "_"
                + conc_str[iii]
            )  # base file name for data file
            cv = pp.potentiostat.CV(
                Eini, Ev1, Ev2, Efin, sr[x], dE, nSweeps, sens, fileName, header
            )
            # Run experiment:
            cv.run()
            data = pp.load_data.CV(fileName + ".txt", folder, model)
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


### Main Power OFF ##################################################################################

print("\n----MAIN POWER OFF----")
power.state("OFF")
time.sleep(10)

print("Finished")
setup.disconnect()



from fileinput import filename
import os
import shutil
import hardpotato as hp
import softpotato as sp
import numpy as np
import pandas as pd
from numpy import savetxt
import scipy
from scipy import stats
import matplotlib.pyplot as plt

model = 'chi760e'

##define path where all current folders are located
parent_path = parent_dir

### generate output
directory = 'output'
path = os.path.join(parent_path, directory)
os.mkdir(path)
print("Directory '% s' created" % directory)
output = str(path)


#### define notation for different concentrations
soln = ['0_uM','250_uM','500_uM','750_uM','1_mM']

### define scanrates
scanrate = [50,100,150,200,250]

# outer loop 'i' identifies folders for each concentration, and list files
for i in soln:
    folder = parent_path + '/FcMeOH_Macros_' + i
    files = os.listdir(folder)
    #### inner loop 'j' goes through listed files and copies them to output path
    for j in files:
        nameOriginal = folder + '/' + str(j)
        shutil.copy2(nameOriginal, output + '/')
        nameMoved = output + '/' + str(j)
        nameNew = output + '/' + str(j)
        os.rename(nameMoved, nameNew)
    outputFiles = os.listdir(output)
    #### inner loop 'k' goes through output files and removes any that are not .txt files
    for k in outputFiles:
        if not str(k).endswith('.txt'):
            os.remove(output + '/'+ str(k))


###setup pstat
model = 'chi760e'
path = 'C:/Potentiostat Path/chi760e.exe'
folder = output
hp.potentiostat.Setup(model=model, path=path, folder=folder)

pad=0.1
w_pad=0.1
h_pad=0.1
title_pad = 2
xlabel_pad = 2
ylabel_pad = 1

soln = ['0_uM','250_uM','500_uM','750_uM','1_mM']
scanrate = [50,100,150,200,250]
concentration = [0.0, 0.25, 0.5, 0.75, 1.0]
fontinfo = {'fontsize': 'medium'}
fontinfo2 = {'fontsize': 'x-small'}


area = 0.000314

###outlier finding and removal test
data_frame = []
concentration = [0.0, 0.25, 0.5, 0.75, 1.0]
for x in range(len(soln)):
    for y in range(len(scanrate)):
        for i in range(8):
            filename = 'Electrode' + str(i+1) + '_CV_' + str(scanrate[y]) + 'mVs_' + str(soln[x]) + '.txt'
            data = hp.load_data.CV(filename,folder,model)
            minpos=(np.argmin(data.i))
            maxpos=(np.argmax(data.i))
            minvalue=(np.amin(data.i))
            maxvalue=(np.amax(data.i))
            current = data.i[:,0].transpose()
            potential=(data.E)
            halfpotential=((data.E[minpos] + data.E[maxpos])/2)
            dE = abs(data.E[minpos] - data.E[maxpos])*1000
            df = pd.DataFrame(data = {'Filename' : filename, 'Concentration / mM' : concentration[x], 'Scanrate / mVs' : scanrate[y],
                                      'Electrode' : i+1, 'Potential Data' : [potential], 'Current Data' : [current], 'Min Current / A' : minvalue,
                                      'Max Current / A' : maxvalue, 'Ehalf / V' : halfpotential, 'dE / mV' : dE, 'Area / cm2' : area, 'Outlier' : 0})
            data_frame.append(df)
fulldata = pd.concat(data_frame, ignore_index=True)

### z test function

def find_outlier(dataframe, threshold):
    threshold = threshold
    mean = np.mean(dataframe)
    std = np.std(dataframe)
    z_scores = np.abs((dataframe - mean) / std)
    return np.where(z_scores > threshold)
    


### find outliers, threshold of >2 standard deviations, 5 passes

for g in ['Max Current / A','Min Current / A','Ehalf / V','dE / mV']:
    for i in range(len(concentration)):
        for j in range(len(scanrate)):
            for f in range(1):
                statsData = fulldata.loc[(fulldata['Scanrate / mVs'] == scanrate[j]) & (fulldata['Concentration / mM'] == concentration[i]) & (fulldata['Outlier'] == 0), g] 
                outliers = find_outlier(statsData, 2)
                outliers = statsData.iloc[outliers]
                fulldata.loc[outliers.index, 'Outlier'] = 1


fulldata.to_csv(path_or_buf=output+'/dataframe.csv')
