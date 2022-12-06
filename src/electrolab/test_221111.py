#from electrolab import *
import controller
import time
# from pypotato import *
import softpotato as sp
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress
import shutil
import serial
import slack
import dill
from pathlib import Path
from dotenv import load_dotenv

import pypotato as pp
import softpotato as sp
from scipy.optimize import curve_fit

import time

t_start = time.time()

# General setup
port = 'COM3'
baud_rate = 115200

setup = controller.Setup(port, baud_rate)
setup.connect()

wait = 10

move = controller.Motor()

# Homming
print('\n----GANTRY HOMING----')
message_home1 = bytes('<homeGantry,0,0>', 'UTF-8')
move.send(message_home1)

print('\n----NOZZLES HOMING----')
message_home2 = bytes('<homeDisp,0,0>', 'UTF-8')
move.send(message_home2)

print('\n----Waiting----')
time.sleep(wait+30)



print('\n----Moving to cell 1----')
pos = controller.Position_in_cell(1)
pos.run()
time.sleep(wait)

##### Operation setup

# rinse = controller.Rinse(wait_time=[16,12,1.5,5,12,16])
# dry = controller.Dry(wait_time=[7,25,7])


##### Execution (1. Dispensing)

print('\n----Moving to cell 5 (dummy)----')
pos = controller.Position_in_cell(5)
pos.run()
time.sleep(wait)

print('\n----Dummy dispense in cell 5 from Nozzle 1 & 2----')
dispense_1 = controller.Dispense(nozzle=1, volume=800, wait_time=[0,3,12,3,0], motor_values=[-39000,100,-8790,100,39000])
dispense_1.run()

dispense_2 = controller.Dispense(nozzle=2, volume=1800, wait_time=[0,3,12,3,0], motor_values=[-39000,100,-9380,100,39000])
dispense_2.run()


print('\n----Moving to cell 1----')
pos = controller.Position_in_cell(1)
pos.run()
time.sleep(wait)

print('\n----Dispense in cell 1 from Nozzle 1 & 2----')
dispense_1 = controller.Dispense(nozzle=1, volume=1000, wait_time=[0,3,12,3,0], motor_values=[-39000,100,-8790,100,39000])
dispense_1.run()

# dispense_2 = controller.Dispense(nozzle=2, volume=500, wait_time=[0,3,12,3,0], motor_values=[-39000,100,-9380,100,39000])
# dispense_2.run()

print('\n----Waiting for 2 mins----')
time.sleep(120)

############ ELECTROCHEMISTRY CODE

###
###
###
###

# path_exe = "C:/Users/Inkyu/Documents/221022_chi/chi760e_LatestUpdate_2021"	 # Path to the chi760e.exe

##### Setup
# Select the potentiostat model to use:
# emstatpico, chi1205b, chi760e
#model = 'chi760e'
model = 'chi1205b' 
#model = 'emstatpico'

# Path to the chi software, including extension .exe. Negletected by emstatpico
path = 'C:/Users/Inkyu/Documents/221022_chi/chi1205b_mini2_LatestUpdate_2022/chi1205b.exe'
# Folder where to save the data, it needs to be created previously
folder = 'C:/Users/Inkyu/Documents/221111_Electrolab_b'
# Initialization:
pp.potentiostat.Setup(model, path, folder)


##### Experimental parameters:
Eini = -0.3     # V, initial potential
Ev1 = 0.5       # V, first vertex potential
Ev2 = -0.3      # V, second vertex potential
Efin = -0.3     # V, final potential
dE = 0.001      # V, potential increment
nSweeps = 2     # number of sweeps
sens = 1e-4     # A/V, current sensitivity
header = 'CV'   # header for data file

##### Experiment:
sr = np.array([0.02, 0.05, 0.1, 0.2])          # V/s, scan rate
nsr = sr.size
i = []
for x in range(nsr):
    # initialize experiment:
    fileName = 'CV_1mM' + str(int(sr[x]*1000)) + 'mVs'# base file name for data file
    cv = pp.potentiostat.CV(Eini, Ev1,Ev2, Efin, sr[x], dE, nSweeps, sens, fileName, header)
    # Run experiment:
    cv.run()
    # load data to do the data analysis later
    data = pp.load_data.CV(fileName + '.txt', folder, model)
    i.append(data.i)
i = np.array(i)
i = i[:,:,0].T
E = data.E


##### Data analysis
# Estimation of D with Randles-Sevcik
n = 1       # number of electrons
A = 0.071   # cm2, geometrical area
#C = 1e-6    # mol/cm3, bulk concentration



###
###
###
###



# input('Should we continue?')
# print('Continuing')
# time.sleep(300)


##### Execution (2. Rinsing)
print('\n----Rinse cell 1----')
rinse = controller.Rinse(wait_time=[16,12,3,20,12,16])
rinse.run()

rinse.run()

##### Execution (3. Drying)
print('\n----Dry----')
dry = controller.Dry(wait_time=[7,25,7])
dry.run()

print('\n----Waiting----')
time.sleep(wait)


print('Finished')
setup.disconnect()

plt.figure(1)
for x in range(len(scanrates)):
    plt.plot(E_measured[x], np.asarray(i_measured[x])*1e6)
sp.plotting.format(xlab='$E$ vs PtQRE / V', ylab='$i$ / $\mu$A', legend=[0], show=1)

plt.figure(2)
plt.plot(srsqrt, iPk*1e6, 'o', label='Experiment')
plt.plot(srsqrt, (lreg.intercept + lreg.slope*srsqrt)*1e6, label='Fitting')
plt.legend()
sp.plotting.format(xlab=r'$\nu^{1/2}$ / V$^{1/2}$ s$^{-1/2}$', ylab='$i_{peak}$ / $\mu$A', legend=[0], show=1)

########## Using D and OCP as input to simulate CV
print('\n##########')
print('Using estimated E0 and D to simulate CV with Soft Potato.')
print('##########')



# CV
wf = sp.technique.Sweep(Eini=Eini, Efin=Ev1, sr=scanrates[1])
twf = wf.t
Ewf = wf.E
e = sp.simulate.E(cRb=concentration*1e-6, cOb=0, E0=np.mean([E_formal]), DO = D, DR = D)
tgrid = sp.simulate.TGrid(twf, Ewf)
xgrid = sp.simulate.XGrid([e], tgrid, Ageo=area)
simE = sp.simulate.Simulate([e], 'E', tgrid, xgrid)
simE.sim()


plt.figure(3)
plt.plot(wf.E, simE.i*1e6, '--', label='Simulation')
plt.plot(E_measured[1], np.asarray(i_measured[1])*1e6, label='Experiment')
plt.legend()
sp.plotting.format(xlab='$E$ vs PtQRE / V', ylab='$i$ / $\mu$A', legend=[1], show=1)


# client.chat_postMessage(channel='C041N144MK4', text="Done! Diffusion Coeffecient = " + str(D))


t_end = time.time()

print((t_end - t_start)/60) # total time in min