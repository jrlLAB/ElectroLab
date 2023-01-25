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

# Main Power ON
print('\n----MAIN POWER ON----')
power.state('ON')
time.sleep(2)

# Homming
print('\n----GANTRY HOMING----')
message_home1 = bytes('<homeGantry,0,0>', 'UTF-8')
move.send(message_home1)
time.sleep(wait+5)

print('\n----NOZZLES HOMING----')
message_home2 = bytes('<homeDisp,0,0>', 'UTF-8')
move.send(message_home2)
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

##### (1) N2 bubbling - nozzle 1 (10 loops for 3 minutes)
print('\n----\033[31mN2 bubbling\033[0m----')
n2_bubbling = controller.N2(loop = 3, nozzle = 1, wait_time = [12,3,12], mode = 'dual')
n2_bubbling.run()

### EC test (in real tests)

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
n2_drying = controller.N2(loop = 10, nozzle = 2, wait_time = [12,3,12], mode = 'single')
n2_drying.run()

### (3) Air Drying - Old version
### move_down / blast / move_up
# print('\n----Dry cell 1----')
# dry = controller.Dry(wait_time=[7,20,7])
# dry.run()

# Main Power OFF
print('\n----MAIN POWER OFF----')
power.state('OFF')
time.sleep(2)

print('Finished')
setup.disconnect()

### <POWER,1,0>
### <PUMP1,1000,45000>
### <PUMP2,1000,45000>