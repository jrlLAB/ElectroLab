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
time.sleep(wait+14)

print('\n----Moving to cell 2----') # to 5
pos = controller.Position_in_cell(2)
pos.run()
time.sleep(wait+5)

##### (1. N2 bubbling)
print('\n----\033[31mN2 dryng\033[0m----')
n2_drying = controller.N2(loop = 5, nozzle = 2, wait_time = [7,6,7], mode = 'single')
n2_drying.run()

time.sleep(wait+5)

print('\n----\033[31mN2 bubbling\033[0m----')
n2_bubbling = controller.N2(loop = 5, nozzle = 1, wait_time = [7,5,7], mode = 'dual')
n2_bubbling.run()

##### (2. Rinsing)
## move_down / <<<LOOP start = suc / flush / equil_flush / suc = LOOP end>>> / move_up

# rinse = controller.Rinse(loop=2, wait_time=[16,12,3.5,12,12,16])
# rinse.run()
# time.sleep(30)

# rinse2 = controller.Rinse(loop=1, wait_time=[16,12,0,20,12,16]) # rinsing without flushing
# rinse2.run()
# time.sleep(wait-5)



print('Finished')
setup.disconnect()