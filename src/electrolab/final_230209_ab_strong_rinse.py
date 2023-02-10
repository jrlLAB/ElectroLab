import controller
import time

# General setup
# port = '/dev/ttyACM0' # Linux
port = 'COM3' # Windows
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
time.sleep(wait+12)

print('\n----GANTRY HOMING----')
message_home1 = bytes('<homeGantry,0,0>', 'UTF-8')
move.send(message_home1)
time.sleep(wait+7)

# print('\n----Moving to cell 5 (dummy)----')
# pos = controller.Position_in_cell(5)
# pos.run()
# time.sleep(wait+5)

# Move to the cell
print('\n----Moving to cell 2----')
pos = controller.Position_in_cell(2)
pos.run()
time.sleep(wait+5)



##### (3) Rinsing
## move_down / <<<LOOP start = suc / flush / equil_flush / suc = LOOP end>>> / move_up

rinse = controller.Rinse(loop=2, wait_time=[16,13,2,5,12,16]) # suction / flushing / suction
rinse.run()
time.sleep(5)

rinse2 = controller.Rinse(loop=1, wait_time=[16,12,0,5,0,16]) # suction only
rinse2.run()
time.sleep(5)



# electrode strong rinsing with bubbling
# (1) filling reservoir with water
rinse3 = controller.Rinse(loop=1, wait_time=[16,0,1,5,0,16]) # change the number of loops
rinse3.run()
time.sleep(5)

# Dummy dispensing (SHOULD BE DONE between rinsing & N2 bubbling, owing to error)
dispense_2 = controller.Dispense(nozzle=2, volume=10, wait_time=[0,3,12,3,0], motor_values=[-39000,80,-8530,80,39000], p = p_linear)
dispense_2.run()
time.sleep(wait)

# (2) N2 bubbling - nozzle 2
print('\n----\033[31mN2 bubbling\033[0m----')
n2_bubbling = controller.N2(loop = 2, nozzle = 2, wait_time = [12,3,12], mode = 'dual')
n2_bubbling.run()
time.sleep(3)

# (3) Suction only
rinse2 = controller.Rinse(loop=1, wait_time=[16,12,0,5,0,16]) # suction only
rinse2.run()
time.sleep(5)

# (CAN BE DONE without dispensing...)

##### (4) N2 drying - nozzle 1 (20 loops for drying at medium flow)
print('\n----\033[31mN2 drying\033[0m----')
n2_drying = controller.N2(loop = 2, nozzle = 1, wait_time = [12,3,12], mode = 'single')
n2_drying.run()
time.sleep(10)


# Main Power OFF
print('\n----MAIN POWER OFF----')
power.state('OFF')
time.sleep(2)

print('Finished')
setup.disconnect()

### <POWER,1,0>
### <PUMP1,1000,45000>
### <PUMP2,1000,45000>