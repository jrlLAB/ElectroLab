import controller
import time

import pypotato as pp
import numpy as np
import matplotlib.pyplot as plt
import softpotato as sp
from scipy.optimize import curve_fit

import os

port = 'COM3'
baud_rate = 115200

setup = controller.Setup(port, baud_rate)
setup.connect()

wait = 10
move = controller.Motor()
power = controller.MainPower()

# Parameters related to peristaltic pumps
p1_default = [19.801938114061617,0.964367848880719,1.167139063529185e-05,-2.873709837738213e-09]
p2_default = [19.751968491759097,0.952312160718057,3.235820687217786e-05,-1.557420164573522e-08]
p_linear = [0,1,0,0]

# Parameters related to liquid volumes & concentrations
conc_tag = np.array([25, 50, 75, 100]) 

# total volume = 1.5 mL
ratio_conc = 1.5
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

for iii in range(len(vol_list_1)):

    # Move to the dummy cell
    print('\n----Moving to cell 4 (dummy)----')
    pos = controller.Position_in_cell(4)
    pos.run()
    time.sleep(wait+5)

    print('\n----Dispense in cell 4 (dummy) from Nozzle 1 & 2----')
    dispense_1d = controller.Dispense(nozzle=1, volume=300, wait_time=[0,3,12,3,0], motor_values=[-39000,80,-8530,80,39000], p = p_linear)
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
    n2_bubbling = controller.N2(loop = 10, nozzle = 2, wait_time = [12,3,12], mode = 'dual')
    n2_bubbling.run()
    time.sleep(7)

    # Main Power OFF (run or skip)
    print('\n----MAIN POWER OFF----')
    power.state('OFF')
    time.sleep(7)


    time.sleep(450)


    
    ##### E-CHEM PART

    ##### Setup
    # Select the potentiostat model to use:
    # emstatpico, chi1205b, chi760e
    #model = 'chi760e'
    model = 'chi1205b'
    #model = 'emstatpico'

    # Path to the chi software, including extension .exe. Negletected by emstatpico
    path = 'C:/Users/Inkyu/Documents/221022_chi/chi1205b_mini2_LatestUpdate_2022/chi1205b.exe'
    # Folder where to save the data, it needs to be created previously
    folder = 'C:/Users/Inkyu/Documents/2023_elab_data/230213_elab_3'                    ### (1) CHANGE THIS !!!!
    # Initialization:
    pp.potentiostat.Setup(model, path, folder)


    ##### Experimental parameters:
    Eini = -0.3     # V, initial potential
    Ev1 = 0.3       # V, first vertex potential
    Ev2 = -0.3      # V, second vertex potential
    Efin = -0.3     # V, final potential
    dE = 0.001      # V, potential increment
    nSweeps = 2     # number of sweeps
    sens = 1e-5     # A/V, current sensitivity                              ### (2) CHANGE THIS !!!!
    header = 'CV'   # header for data file


    ##### Experiment:
    sr = np.array([0.02, 0.05, 0.1, 0.2, 0.5])          # V/s, scan rate
    # [0.02, 0.04, 0.06, 0.08, 0.1, 0.12, 0.14, 0.16, 0.18, 0.2]
    nsr = sr.size
    i = []
    for x in range(nsr):
        # initialize experiment:
        fileName = 'CV_' + str(int(sr[x]*1000)) + 'mVs' + '_'+ str(int(conc_tag[iii]))# base file name for data file
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
    C = 1e-6    # mol/cm3, bulk concentration                                  ### (3) CHANGE THIS !!!!

    # Showcases how powerful softpotato can be for fitting:
    def DiffCoef(sr, D):
        macro = sp.Macro(n, A, C, D)
        rs = macro.RandlesSevcik(sr)
        return rs
        
    iPk_an = np.max(i, axis=0)
    iPk_ca = np.min(i, axis=0)
    iPk = np.array([iPk_an, iPk_ca]).T
    popt, pcov = curve_fit(DiffCoef, sr, iPk_an)
    D = popt[0]

    # Estimation of E0 from all CVs:
    EPk_an = E[np.argmax(i, axis=0)]
    EPk_ca = E[np.argmin(i, axis=0)]
    E0 = np.mean((EPk_an+EPk_ca)/2)

    #### Simulation with softpotato
    iSim = []
    for x in range(nsr):
        wf = sp.technique.Sweep(Eini,Ev1, sr[x])
        sim = sp.simulate.E(wf, n, A, E0, 0, C, D, D)
        sim.run()
        iSim.append(sim.i)
    iSim = np.array(iSim).T
    print(iSim.shape)
    ESim = sim.E

    ##### Printing results
    print('\n\n----------Results----------')
    print('D = {:.2f}x10^-6 cm2/s'.format(D*1e6))
    print('E0 = {:.2f} mV'.format(E0*1e3))

    ##### Plotting
    srsqrt = np.sqrt(sr)
    sp.plotting.plot(E, i*1e6, ylab='$i$ / $\mu$A', fig=1, show=0)
    sp.plotting.plot(srsqrt, iPk*1e6, mark='o-', xlab=r'$\nu^{1/2}$ / V$^{1/2}$ s$^{-1/2}$', 
                    ylab='$i$ / $\mu$A', fig=2, show=0)

    plt.figure(3)
    plt.plot(E, i*1e6)
    plt.plot(wf.E, iSim*1e6, 'k--')
    plt.title('Experiment (-) vs Simulation (--)')
    sp.plotting.format(xlab='$E$ / V', ylab='$i$ / $\mu$A', legend=[0], show=0) # show 0 or 1





    # Main Power ON
    print('\n----MAIN POWER ON----')
    power.state('ON')
    time.sleep(5)

    ##### (2) Initial Electrode Rinsing
    ## move_down / <<<LOOP start = suc / flush / equil_flush / suc = LOOP end>>> / move_up

    rinse = controller.Rinse(loop=4, wait_time=[16,13,2,5,12,16]) # change the number of loops
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
    n2_bubbling = controller.N2(loop = 7, nozzle = 2, wait_time = [12,3,12], mode = 'dual')
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