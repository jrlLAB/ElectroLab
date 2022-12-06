#from electrolab import *
import controller
import time
from pypotato import *
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

# General setup
port = 'COM3'
baud_rate = 115200

setup = controller.Setup(port, baud_rate)
setup.connect()

wait = 10

move = controller.Motor()

# Gantry Homming
print('\n----GANTRY HOMING----')
message_home1 = bytes('<homeGantry,0,0>', 'UTF-8')
move.send(message_home1)

##### (0. Additional suction)
print('\n----Initializing Nozzles----')
message_equil_f = b'<DC5, 255, 4000>'
move.send(message_equil_f)
time.sleep(3)

message_suc = bytes('<DC2, 210, 5000>', 'UTF-8')
move.send(message_suc)

print('\n----Waiting----')
time.sleep(10)

move.send(message_suc)

print('\n----Waiting----')
time.sleep(3)

# Nozzle Homming

print('\n----NOZZLES HOMING----')
message_home2 = bytes('<homeDisp,0,0>', 'UTF-8')
move.send(message_home2)

print('\n----Waiting----')
time.sleep(wait+15)

print('\n----Moving to cell 1----')
pos = controller.Position_in_cell(3)
pos.run()
time.sleep(wait)

##### Operation setup
dispense_1st_init = controller.Dispense(nozzle=1,motor_values=[-39000,150,-9100,39000],wait_time=[47,3,0,0])

dispense_1st_1ml_a = controller.Dispense(nozzle=1,motor_values=[-39000,150,-9100,39000],wait_time=[0,0,0,0])
dispense_1st_1ml_b = controller.Dispense(nozzle=1,motor_values=[-39000,150,-9100,39000],wait_time=[0,3,0,0])
dispense_1st_1ml_c = controller.Dispense(nozzle=1,motor_values=[-39000,150,-9100,39000],wait_time=[0,0,11,0])

dispense_1st_final = controller.Dispense(nozzle=1,motor_values=[-39000,150,-9100,39000],wait_time=[0,0,0,47])

rinse = controller.Rinse(wait_time=[16,12,1.5,5,12,16])
dry = controller.Dry(wait_time=[7,25,7])


##### Execution (1. Dispensing)

print('\n----Nozzle 1 disp. 1 mL----')
dispense_1st_1ml_a.run()
time.sleep(3)
dispense_1st_1ml_b.run()
time.sleep(3)
dispense_1st_1ml_c.run()
time.sleep(12)

############ ELECTROCHEMISTRY CODE

###
###
###
###


################ Directory Setup ####################

directory = "FcMeOH_3"

######################### EXPERIMENT INFO ########################
expInfo = "1 mM FcMeOH, 100 mM KNO3, Screen Printed Electrode"
##################################################################

# Parent Directory path
parent_dir = "C:/Users/Inkyu/Documents/221022_Electrolab"
# Path
path = os.path.join(parent_dir, directory)
os.mkdir(path)
print("Directory '% s' created" % directory)
folder = str(path)

#####################################################

#### Potentiostat setup #####
model = 'chi760e'			 # Model to use
path_exe = "C:/Users/Inkyu/Documents/221022_chi/chi760e_LatestUpdate_2021"	 # Path to the chi760e.exe
potentiostat.Setup(model, path_exe, folder)	 # Setup


# generate filename with timestring
copied_script_name = time.strftime("%Y-%m-%d_%H%M") + '_' + os.path.basename(__file__)

# copy script
shutil.copy(__file__, folder + os.sep + copied_script_name) 


##### This is an extra feature that uses the Slack App to alert the user when the experiment is done, it can be deleted if irrelevant
# env_path = Path('.') / '.env'
# load_dotenv(dotenv_path=env_path)
# client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
# #send notification to slack that run has started
# client.chat_postMessage(channel='C041N144MK4', text="Running: " + expInfo)
#####


###Define Experimental Parameters

### Electrode area cm^2 
area = 0.071

### Sensitivity in A
sens = 1e-5

### Concentrations in mM
concentration = np.array([0.8])

### Scan rate in V/s
scanrates = [0.05,0.1,0.25,0.5]

E_measured = []
i_measured = []
E_formal = []

#change concentrations
for x in concentration:

    ##### Running OCP 1
    st = 10     # s, total time
    eh = 1      # V, high limit of potential
    el = -1     # V, low limit of potential
    si = 1e-2   # s, time interval
    fileName_OCP = 'OCP_' + str(int(x))
    print('Running OCP with concentration of ' + str(int(x)))
    ocp = potentiostat.OCP(ttot=st, dt=si, fileName=fileName_OCP)    
    #ocp = chi.OCP(st=st, eh=eh, el=el, si=si,
    #              folder=folder, fileName=fileName_OCP)
    ocp.run()
    # Loading data and plotting it:
    data = np.loadtxt(folder+'/'+fileName_OCP+'.txt', skiprows=13, delimiter=',')
    t = data[:,0]
    E = data[:,1]

    E_ocp = E[-1]
    Eini = E_ocp - 0.3
    Ev1 = E_ocp + 0.4
    sens = 1e-5


    for n in range(len(scanrates)):
        ##### Running Generator Only CV
        Ei = Eini         # V, initial potential
        Eh = Ev1        # V, higher potential
        El = Eini      # V, lower potential
        sr = scanrates[n]        # V/s, scan rate
        fileName_CV = 'CV_' + str(int(x)) + '_' + str(int(sr*1000)) + '_mVs-1'
        print('Running CV at scanrate of ' + str(int(sr*1000)) + '_mVs-1')
        cv = potentiostat.CV(Eini=Ei, Ev1=Eh, Ev2=El, Efin=El, sr=sr, sens=sens, dE=0.001,
                            fileName=fileName_CV)
        #cv = chi.CV(Ei=Ei, Eh=Eh, El=El, sr=sr, sens=sens, bipot=0, 
        #              folder=folder, fileName=fileName_CV)
        cv.run()

        #load data new method
        data = load_data.CV(fileName_CV + '.txt', folder, model)
        E_measured.append(data.E)
        i_measured.append(-data.i)

        #get E formal
        E_cat = E_measured[n][np.argmin(i_measured[n])]
        E_an = E_measured[n][np.argmax(i_measured[n])]
        E_formal.append((E_cat+E_an)/2)

        print('Eformal = ' + str(E_formal) + ' V')
        
        ##### Running OCP 1
        st = 30     # s, total time
        eh = 1      # V, high limit of potential
        el = -1     # V, low limit of potential
        si = 1e-2   # s, time interval
        fileName_OCP = 'OCP1_' + str(int(x))
        print('Running OCP with Generator of IDA ' + str(int(x)))
        ocp = potentiostat.OCP(ttot=st, dt=si, fileName=fileName_OCP)    
        #ocp = chi.OCP(st=st, eh=eh, el=el, si=si,
        #              folder=folder, fileName=fileName_OCP)
        ocp.run()           

    srsqrt = np.sqrt(np.asarray(scanrates))
    iPk = np.max(i_measured, axis=1).T[0]
    C = concentration*1e-6 # mol/cm3, bulk concentration
    lreg = linregress(srsqrt, iPk)
    D = (lreg.slope/(2.69e5*area*C))**2

    print(str(D))






###
###
###
###



# input('Should we continue?')
# print('Continuing')
# time.sleep(300)


##### Execution (2. Rinsing)
print('\n----Rinsing----')
rinse.run()

##### (2a. Additional suction)
print('\n----Suction----')
message_equil_f = b'<DC5, 255, 4000>'
move.send(message_equil_f)
time.sleep(3)

message_suc = bytes('<DC2, 210, 5000>', 'UTF-8')
move.send(message_suc)

print('\n----Waiting----')
time.sleep(10)

move.send(message_suc)

print('\n----Waiting----')
time.sleep(3)

message_drip_suc = bytes('<PUMP1, 1000, 150>', 'UTF-8')
move.send(message_drip_suc)
time.sleep(3)

move.send(message_equil_f)
time.sleep(3)

##### 2b. Additional Suction
print('\n----Suction----')
message_add_s_1 = b'<ZFLUSH, 100, +60000>' # move down
move.send(message_add_s_1)
time.sleep(16)

message_add_s_2 = bytes('<DC2, 210, 20000>', 'UTF-8') # suction
move.send(message_add_s_2)
time.sleep(12)

message_add_s_3 = bytes('<ZFLUSH, 100, -60000>', 'UTF-8') # move up
move.send(message_add_s_3)
time.sleep(16)



##### Execution (3. Drying)
print('\n----Drying----')
dry.run()

print('\n----Waiting----')
time.sleep(wait)




##### (4. Additional suction)
# print('\n----Moving to the Dummy Reservoir----')
# pos11 = controller.Position_in_cell(4)
# pos11.run()
# time.sleep(wait)

# change = controller.Nozzle_change(3,2,10)
# change.run()
# time.sleep(wait)

print('\n----Reinitializing Nozzles----')
message_equil_f = b'<DC5, 255, 4000>'
move.send(message_equil_f)
time.sleep(3)

message_suc = bytes('<DC2, 210, 5000>', 'UTF-8')
move.send(message_suc)

print('\n----Waiting----')
time.sleep(10)

move.send(message_suc)

print('\n----Waiting----')
time.sleep(3)

message_drip_suc = bytes('<PUMP1, 1000, 150>', 'UTF-8')
move.send(message_drip_suc)
time.sleep(3)

move.send(message_equil_f)
time.sleep(3)



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


