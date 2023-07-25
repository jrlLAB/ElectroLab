import controller
import time

from hardpotato import *
import numpy as np
import matplotlib.pyplot as plt
import softpotato as sp
from scipy.optimize import curve_fit
import os
from scipy.stats import linregress
import serial
import time
from pathlib import Path
import pandas as pd
import random
import shutil
import datetime

start_time = time.time()

####define com ports for controller and MUX + baudrate (keep at 115200 for both)
controllerPort = "COM5"

baud_rate = 115200

###setup controller
setup = controller.Setup(controllerPort, baud_rate)
setup.connect()


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


# total volume = 1.0 mL (total volume = ratio_conc * 1 mL)
ratio_conc = 0.8  # (owing to reservoir size + ACN surface tension)


###shuffle concentrations
pre_list_1 = [1500, 1350, 1200, 1050, 900, 750, 600, 450, 300, 150, 0]
random.shuffle(pre_list_1)
vol_list_1 = [x * ratio_conc for x in pre_list_1]
vol_list_2 = [(1500 - x) * ratio_conc for x in pre_list_1]
print(vol_list_1)
print(vol_list_2)

##write file with concentrations for future referencing
text_file = open(f"{parent_folder}/shuffled_order.txt", "w")
write_text = str(pre_list_1).replace("[", "").replace("]", "").replace(", ", "\n")
n = text_file.write(write_text)
text_file.close()

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
            speed=8000,
            wait_time=[0, 3, 26.4, 3, 0],
            motor_values=[-9000, 20, -2755, 20, 9000],
            p=p1_new,
        )
        print(f"From nozzle 2, dispensing \033[31m{y} \033[0muL  \n")
        dispense_2d.run()
        time.sleep(wait)
    else:
        dispense_2d = controller.Dispense(
            nozzle=2,
            volume=y,
            speed=8000,
            wait_time=[0, 3, 26.4, 3, 0],
            motor_values=[-9000, 20, -2755, 20, 9000],
            p=p_linear,
        )
        print(f"From nozzle 2, dispensing \033[33m{y} \033[0muL  \n")
        dispense_2d.run()
        time.sleep(wait)

    print(
        f"Redoxmer (RAP) + Electrolyte (TBA) \033[33m{x} \033[0muL and Electrolyte \033[33m{y} \033[0muL has been dispensed \n"
    )

    ### Argon short bubbling (to avoid excessive evaporation)##########
    print("\n----\033[31mN2 bubbling\033[0m----")
    n2_bubbling = controller.N2_short(
        loop=1, nozzle=2, wait_time=[12, 3, 12], mode="dual"
    )
    n2_bubbling.run()
    time.sleep(2)

    ### Main Power OFF #################################################################
    print("\n----MAIN POWER OFF----")
    power.state("OFF")
    time.sleep(15)

    ############# E-CHEM PART ###############################################

    ################ Directory Setup ####################

    directory = f"mix_{iii+1}"

    ######################### EXPERIMENT INFO ########################
    expInfo = f"mix 0.5 mM FeRAP, 0 mM TBAPF6 and 500 mM TBAPF6, 100 mM KNO3, single 25 um gold UME"
    ##################################################################
    print(expInfo)
    path = os.path.join(parent_folder, directory)
    os.mkdir(path)
    print("Directory '% s' created" % directory)
    folder = str(path)
    #####################################################

    ##### Setup
    # Select the potentiostat model to use:
    # emstatpico, chi1205b, chi760e
    #### Potentiostat setup #####
    model = "chi760e"  # Model to use
    path_exe = "C:/Potentiostat Path/chi760e.exe"  # Path to the chi760e.exe
    potentiostat.Setup(model, path_exe, folder)  # Setup

    ##### Running OCP 1
    st = 120  # s, total time
    eh = 1  # V, high limit of potential
    el = -1  # V, low limit of potential
    si = 1e-2  # s, time interval
    fileName_OCP = f"OCP"
    print(f"Running OCP")
    ocp = potentiostat.OCP(ttot=st, dt=si, fileName=fileName_OCP)
    ocp.run()
    data = load_data.OCP(f"{fileName_OCP}.txt", folder, model)

    for x in range(1):
        # CV
        Ei = 0  # V, initial potential
        Eh = 0.7  # V, higher potential
        El = 0  # V, higher potential
        sr = 0.005  # V/s, scan rate
        sens = 1e-9  # V/A, sensitivity
        fileName_CV = f"CV_{x+1}"
        print(f"Running CV {x+1}")
        cv = potentiostat.CV(
            Eini=Ei,
            Ev1=Eh,
            Ev2=El,
            Efin=Ei,
            sr=sr,
            sens=sens,
            dE=0.001,
            nSweeps=2,
            fileName=fileName_CV,
        )
        cv.run()
        data = load_data.CV(f"{fileName_CV}.txt", folder, model)

        # it
        Estep = Eh  # V, step potential
        dt = 0.1  # s, time increment
        ttot = 60  # s, total time
        sens = 1e-9  # A/V, current sensitivity
        fileName_IT = f"IT_{x+1}"
        print(f"Running IT {x+1}")
        ca = potentiostat.CA(
            Estep=Estep, dt=dt, ttot=ttot, sens=sens, qt=2, fileName=fileName_IT
        )
        # Run experiment:
        ca.run()
        data = load_data.CA(f"{fileName_IT}.txt", folder, model)

    print("Done!")

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

print("\n----\033[31m Print the total time duration \033[0m----")
end_time = time.time()
total_time = end_time - start_time
total_time_list = str(datetime.timedelta(seconds=total_time)).split(".")
print(total_time_list[0])  # Hrs:Mins:Secs format


from fileinput import filename
import os
import shutil
import hardpotato as hp
import numpy as np
import pandas as pd
from numpy import savetxt
import scipy
from scipy import stats
import matplotlib.pyplot as plt
from outliers import smirnov_grubbs as grubbs



##define path where all current folders are located
parent_path = parent_dir1

num_runs = 1
num_folders = 9
num_experiments = 1




##make output path
subfolders = os.listdir(parent_path)
if 'output' in subfolders:
    print('Output exists already, not creating')
    output = f'{parent_path}/output'
else:
    directory = 'output'
    path = os.path.join(parent_path, directory)
    os.mkdir(path)
    print("Directory '% s' created" % directory)
    output = f'{path}'

run_name = 'expt'
folder_name = 'mix'



###identifies all folders
for g in range(num_runs):
    ##copy shuffled order to output for each expt
    if not f'{run_name}{g+1}_shuffled_order.txt' in os.listdir(output):
        shutil.copy2(f'{parent_path}/{run_name}{g+1}/shuffled_order.txt', output)
        os.rename(f'{output}/shuffled_order.txt',f'{output}/{run_name}{g+1}_shuffled_order.txt')
    ### outer loop 'i' identifies all folders for defined naming scheme, and list files
    for i in range(num_folders):
    #### inner loop 'j' goes through listed files and copies them to output path, removing any none txt files, and not copying over new ones if they exist
        for j in os.listdir(f'{parent_path}/{run_name}{g+1}/{folder_name}_{i+1}'):
            if f'{parent_path}/{folder_name}_{i+1}/{j}'.endswith('.txt'):
                if not f'{run_name}{g+1}_{folder_name}{i+1}_{j}' in os.listdir(output):
                    shutil.copy2(f'{parent_path}/{run_name}{g+1}/{folder_name}_{i+1}/{j}', output)
                    os.rename(f'{output}/{j}',f'{output}/{run_name}{g+1}_{folder_name}{i+1}_{j}')

###setup pstat
model = 'chi760e'
path = 'C:/Potentiostat Path/chi760e.exe'
folder = output
hp.potentiostat.Setup(model=model, path=path, folder=folder)

###conc function, part= experiment in cycle, total = total cycles
def conc_fxn(conc_a, conc_b, part, total):
    conc_value = (conc_b*((total)-part)+conc_a*(part))/(total)
    return conc_value


######################## CVs ################
data_frame_CV = []
data_frame_IT = []
for z in range(num_runs):
    
    ###this defines the order of concentrations by importing "shuffed_order.txt"
    with open(f'{output}/{run_name}{z+1}_shuffled_order.txt') as file:
        mix_to_conc = [float(line.rstrip()) for line in file]

    for x in range(num_folders):
        for y in range(num_experiments):
            #CVs to dataframe
            #print(conc_fxn(1,500,x,num_folders))
            filename_CV = f'expt{z+1}_mix{x+1}_CV_{y+1}.txt'
            data_CV = hp.load_data.CV(filename_CV,folder,model)
            potential_CV = data_CV.E
            current_CV = data_CV.i[:,0].transpose()
            df_CV = pd.DataFrame(data = {'Filename' : filename_CV, 'Concentration / mM' : conc_fxn(1,500,mix_to_conc[x],1500),
                                        'Potential Data' : [potential_CV], 'Current Data' : [current_CV], 'Min Current / A' : np.amin(data_CV.i),
                                        'Max Current / A' : np.amax(data_CV.i), 'Run' : x+1, 'Expt' : z+1, 'Variance' : 0})
            data_frame_CV.append(df_CV)
            ###IT to dataframe
            filename_IT = f'expt{z+1}_mix{x+1}_IT_{y+1}.txt'
            data_IT = hp.load_data.CA(filename_IT,folder,model)
            time_IT = data_IT.t
            current_IT = data_IT.i
            df_IT = pd.DataFrame(data = {'Filename' : filename_IT, 'Concentration / mM' : conc_fxn(1,500,mix_to_conc[x],1500),
                                        'Time Data' : [time_IT], 'Current Data' : [current_IT], 'Steady State' : data_IT.i[-1], 'Run' : x+1, 'Expt' : z+1})
            data_frame_IT.append(df_IT)

fulldata_CV = pd.concat(data_frame_CV, ignore_index=True)
fulldata_IT = pd.concat(data_frame_IT, ignore_index=True)
fulldata_CV.to_csv(path_or_buf=f'{output}/dataframe_CV.csv')
fulldata_IT.to_csv(path_or_buf=f'{output}/dataframe_IT.csv')




