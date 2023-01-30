import controller
import time

import pypotato as pp
import numpy as np
import matplotlib.pyplot as plt
import softpotato as sp
from scipy.optimize import curve_fit

port = 'COM3'
baud_rate = 115200

setup = controller.Setup(port, baud_rate)
setup.connect()

wait = 10
move = controller.Motor()
power = controller.MainPower()

p1_default = [19.801938114061617,0.964367848880719,1.167139063529185e-05,-2.873709837738213e-09]
p2_default = [19.751968491759097,0.952312160718057,3.235820687217786e-05,-1.557420164573522e-08]
p_linear = [0,1,0,0]

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

# Move to the dummy cell
print('\n----Moving to cell 4 (dummy)----')
pos = controller.Position_in_cell(4)
pos.run()
time.sleep(wait+5)

print('\n----Dispense in cell 4 (dummy) from Nozzle 1 & 2----')

dispense_1d = controller.Dispense(nozzle=1, volume=400, wait_time=[0,3,12,3,0], motor_values=[-39000,80,-8530,80,39000], p = p_linear)
dispense_1d.run()
time.sleep(wait-3)

dispense_2d = controller.Dispense(nozzle=2, volume=400, wait_time=[0,3,12,3,0], motor_values=[-39000,80,-9300,80,39000], p = p_linear)
dispense_2d.run()
time.sleep(wait-3)



# Move to the cell
print('\n----Moving to cell 2----')
pos = controller.Position_in_cell(2)
pos.run()
time.sleep(wait+5)

### Nozzle 1 contains redoxmer !!
# p1_default, p2_default, p_linear

### (0) CHANGE VOLUMES !!!!
print('\n----Dispense in cell 2 from Nozzle 1 & 2----')

# REDOX SPECIES + ELECTROLYTES
dispense_1 = controller.Dispense(nozzle=1, volume=1000, wait_time=[0,3,12,3,0], motor_values=[-39000,80,-8530,80,39000], p = p_linear)
dispense_1.run()
time.sleep(wait)

# ELECTROLYTES
dispense_2 = controller.Dispense(nozzle=2, volume=500, wait_time=[0,3,12,3,0], motor_values=[-39000,80,-9300,80,39000], p = p_linear)
dispense_2.run()
time.sleep(wait)

##### (1) N2 bubbling - nozzle 1 (10 loops for 3 minutes)
print('\n----\033[31mN2 bubbling\033[0m----')
n2_bubbling = controller.N2(loop = 3, nozzle = 2, wait_time = [12,3,12], mode = 'dual')
n2_bubbling.run()
time.sleep(3)

# Main Power OFF (run or skip)
print('\n----MAIN POWER OFF----')
power.state('OFF')
time.sleep(5)





# Main Power ON
print('\n----MAIN POWER ON----')
power.state('ON')
time.sleep(2)

##### (2) Rinsing
## move_down / <<<LOOP start = suc / flush / equil_flush / suc = LOOP end>>> / move_up

rinse = controller.Rinse(loop=2, wait_time=[16,12,3.5,12,12,16]) # change the number of loops
rinse.run()
time.sleep(5)

rinse2 = controller.Rinse(loop=1, wait_time=[16,12,0,20,12,16]) # rinsing without flushing
rinse2.run()
time.sleep(wait-5)

##### (3) N2 drying - nozzle 2 (20 loops for drying at medium flow)
print('\n----\033[31mN2 drying\033[0m----')
n2_drying = controller.N2(loop = 5, nozzle = 1, wait_time = [12,3,12], mode = 'single')
n2_drying.run()
time.sleep(3)

# Main Power OFF (run or skip)
print('\n----MAIN POWER OFF----')
power.state('OFF')
time.sleep(2)

print('Finished')
setup.disconnect()

### <POWER,1,0>
### <PUMP1,1000,45000>
### <PUMP2,1000,45000>