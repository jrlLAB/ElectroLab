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
time.sleep(wait+5)

print('\n----NOZZLES HOMING----')
message_home2 = bytes('<homeDisp,0,0>', 'UTF-8')
move.send(message_home2)
time.sleep(wait+7)

print('\n----Moving to cell 2----')
pos = controller.Position_in_cell(2)
pos.run()
time.sleep(wait+5)

##### (1. N2 bubbling)
print('\n----N2 bubbling----')
n2_bubbling = controller.N2(nozzle = 1, wait_time = [7,5,7])
n2_bubbling.run()



print('Finished')
setup.disconnect()