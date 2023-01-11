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
time.sleep(wait+10)

print('\n----Moving to cell 2----') # to 5
pos = controller.Position_in_cell(2)
pos.run()
time.sleep(wait+5)

# print('\n----Disp. 1 init_a----')
# dispense_fill_1 = controller.Dispense(nozzle=1, volume=4500, wait_time=[47,3,0,3,0], motor_values=[-39000,80,-8530,80,39000], p = [0,1,0,0])
# dispense_fill_1.run()

# print('\n----Dispense in cell 5 from Nozzle 1 & 2----')
# dispense_1d = controller.Dispense(nozzle=1, volume=500, wait_time=[0,3,12,3,0], motor_values=[-39000,80,-8530,80,39000])
# dispense_1d.run()
# time.sleep(wait-3)

##### (1. N2 bubbling)
print('\n----N2 bubbling----')
n2_bubbling = controller.N2(loop = 2, nozzle = 1, wait_time = [7,5,7])
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