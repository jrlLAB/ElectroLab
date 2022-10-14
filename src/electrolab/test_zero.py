import controller
import time

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
dispense_1st_init = controller.Dispense(nozzle=1,motor_values=[-39000,150,-9100,39000],wait_time=[47,3,0,0])
dispense_1st_1ml = controller.Dispense(nozzle=1,motor_values=[-39000,150,-9100,39000],wait_time=[0,3,11,0])
dispense_1st_final = controller.Dispense(nozzle=1,motor_values=[-39000,150,-9100,39000],wait_time=[0,0,0,47])

rinse = controller.Rinse(wait_time=[16,12,1.5,5,12,16])

dry = controller.Dry(wait_time=[7,25,7])


##### Execution (1. Dispensing)
# print('\n----Nozzle 1 initialization----')
# dispense_1st_init.run()

print('\n----Nozzle 1 disp. 1 mL----')
dispense_1st_1ml.run()

# print('\n----Nozzle 1 emptying the tube----')
# dispense_1st_final.run()



##### Execution (2. Rinsing)
print('\n----Rinsing----')
rinse.run()



##### Execution (3. Drying)
# print('\n----Moving to cell 1----')
print('\n----Drying----')
dry.run()

print('\n----Waiting----')
time.sleep(wait)

# dispense_later.run()

print('\n----Moving to cell 2----')
pos = controller.Position_in_cell(2)
pos.run()
time.sleep(wait)

print('\n----Nozzle 1 disp. 1 mL----')
dispense_1st_1ml.run()

print('Finished')
setup.disconnect()