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
vol_list_1 = [10]
vol_list_2 = [10]

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

    # Move to the cell
print('\n----Moving to cell 2----')
pos = controller.Position_in_cell(2)
pos.run()
time.sleep(wait+5)


# Dummy dispensing (SHOULD BE DONE between rinsing & N2 bubbling, owing to error)
dispense_2 = controller.Dispense(nozzle=2, volume=10, wait_time=[0,3,12,3,0], motor_values=[-39000,80,-8530,80,39000], p = p_linear)
dispense_2.run()
time.sleep(wait)

    
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
time.sleep(7)


# Main Power OFF (run or skip)
print('\n----MAIN POWER OFF----')
power.state('OFF')
time.sleep(5)

print('Finished')
setup.disconnect()

### <POWER,1,0>
### <PUMP1,1000,45000>
### <PUMP2,1000,45000>