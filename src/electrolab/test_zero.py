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

# print('\n----Moving to cell 1----')
# pos = controller.Position_in_cell(1)
# pos.run()
# time.sleep(wait)

##### Operation setup
dispense_1st = controller.Dispense(nozzle=1,motor_values=[-39000,150,-9100,39000],wait_time=[47,1,11,47])
dispense_later = controller.Dispense(nozzle=1,motor_values=[-39000,150,-9100,39000],wait_time=[0,1,11,0])
rinse = controller.Rinse(wait_time=[16,12,1.5,5,12,16])
dry = controller.Dry(wait_time=[7,25,7])

# dispense.run()
# rinse.run()

##### Execution (3. Drying)
# print('\n----Moving to cell 1----')
# dry.run()

##### Execution (2. Rinsing)
# rinse.run()

##### Execution (1. Dispensing)
dispense_1st.run()

print('\n----Waiting----')
time.sleep(wait)

# dispense_later.run()

print('Finished')
setup.disconnect()