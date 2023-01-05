import controller
import time

# General setup
port = 'COM3'
baud_rate = 115200

setup = controller.Setup(port, baud_rate)
setup.connect()

wait = 10

move = controller.Motor()

# <PUMP1,1000,60000>
# <PUMP2,1000,60000>

# Homming
print('\n----GANTRY HOMING----')
message_home1 = bytes('<homeGantry,0,0>', 'UTF-8')
move.send(message_home1)
time.sleep(wait+5)

print('\n----NOZZLES HOMING----')
message_home2 = bytes('<homeDisp,0,0>', 'UTF-8')
move.send(message_home2)
time.sleep(wait+7)

print('\n----Moving to cell 5 (dummy)----')
pos = controller.Position_in_cell(5)
pos.run()
time.sleep(wait+5)

##### Operation setup
dispense = controller.Dispense(nozzle=1, volume=1000, wait_time=[0,3,11,3,0], motor_values=[-39000,150,-9100,150,39000])
rinse = controller.Rinse(wait_time=[16,12,1.5,5,12,16])
dry = controller.Dry(wait_time=[7,25,7])

##### (1. Filling tube in dispenser 1)
## init / remove_drip / dispense / remove_drip2 / idle

print('\n----Disp. 1 init_a----')
dispense_fill_1 = controller.Dispense(nozzle=1, volume=4500, wait_time=[47,3,0,3,0], motor_values=[-39000,80,-8530,80,39000])
dispense_fill_1.run()

dispense_1 = controller.Dispense(nozzle=1, volume=300, wait_time=[0,3,12,3,0], motor_values=[-39000,80,-8530,80,39000])
dispense_1.run()

dispense_fill_2 = controller.Dispense(nozzle=2, volume=4500, wait_time=[47,3,0,3,0], motor_values=[-39000,80,-9230,80,39000])
dispense_fill_2.run()

dispense_2 = controller.Dispense(nozzle=2, volume=300, wait_time=[0,3,12,3,0], motor_values=[-39000,80,-9230,80,39000])
dispense_2.run()

# dispense_empty = controller.Dispense(nozzle=1, volume=1000, wait_time=[0,0,0,0,47], motor_values=[-39000,150,-9100,150,39000])
# dispense_empty.run()

# <PUMP1,1000,45000>
# <PUMP2,1000,45000>

##### (2. Rinsing)
## move_down / suc / flush / equil_flush / suc / move_up
# rinse_init = controller.Rinse(wait_time=[16,12,0,5,0,16])
# rinse_init.run()

# print('\n----Waiting before additional suction---')
# time.sleep(12)

##### (3. Drying)
## move_down / blast / move_up
# dry = controller.Dry(wait_time=[7,20,7])
# dry.run()

##### (4. Move back to Cell 1)
print('\n----Moving to cell 1----')
pos = controller.Position_in_cell(1)
pos.run()
time.sleep(wait)

print('Finished')
setup.disconnect()