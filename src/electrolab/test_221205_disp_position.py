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

# Homming
print('\n----GANTRY HOMING----')
message_home1 = bytes('<homeGantry,0,0>', 'UTF-8')
move.send(message_home1)

print('\n----NOZZLES HOMING----')
message_home2 = bytes('<homeDisp,0,0>', 'UTF-8')
move.send(message_home2)

print('\n----Moving to cell 1----')
pos = controller.Position_in_cell(1)
pos.run()
time.sleep(wait)

print('\n----Dispense in cell 1 from Nozzle 1 & 2----')
dispense_1 = controller.Dispense(nozzle=1, volume=300, wait_time=[0,3,12,3,0], motor_values=[-39000,80,-8530,80,39000])
dispense_1.run()
time.sleep(10)

time.sleep(10)

dispense_2 = controller.Dispense(nozzle=2, volume=300, wait_time=[0,3,12,3,0], motor_values=[-39000,80,-9300,80,39000])
dispense_2.run()
time.sleep(10)

##### (2. Rinsing)
## move_down / suc / flush / equil_flush / suc / move_up
print('\n----Rinse cell 1----')
rinse = controller.Rinse(wait_time=[16,12,3.5,20,12,16])
rinse.run()

rinse2 = controller.Rinse(wait_time=[16,12,0,6,12,16])
rinse2.run()

#### (3. Drying)
# move_down / blast / move_up
print('\n----Dry cell 1----')
dry = controller.Dry(wait_time=[7,15,7])
dry.run()


# <PUMP1,1000,45000>
# <PUMP2,1000,45000>

# Homming
# print('\n----HOMMING----')
# message_home = bytes('<homeGantry,0,0>', 'UTF-8')
# move.send(message_home)
# time.sleep(wait)

print('Finished')
setup.disconnect()
