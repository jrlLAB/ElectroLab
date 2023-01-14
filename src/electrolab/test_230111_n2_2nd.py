import controller
import time

# General setup
port = 'COM3'
baud_rate = 115200

p1_default = [19.801938114061617,0.964367848880719,1.167139063529185e-05,-2.873709837738213e-09]
p2_default = [19.751968491759097,0.952312160718057,3.235820687217786e-05,-1.557420164573522e-08]
p_linear = [0,1,0,0]

setup = controller.Setup(port, baud_rate)
setup.connect()
wait = 10

move = controller.Motor()
power = controller.MainPower()

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
time.sleep(wait+14)

print('\n----Moving to cell 5----')
pos = controller.Position_in_cell(5)
pos.run()
time.sleep(wait+5)

power.state('OFF')
time.sleep(2)

power.state('ON')
time.sleep(2)

print('\n----Moving to cell 2----') # to 5
pos = controller.Position_in_cell(2)
pos.run()
time.sleep(wait+5)

##### (N2 bubbling - nozzle 1 // 10 loops for )
print('\n----\033[31mN2 bubbling\033[0m----')
n2_bubbling = controller.N2(loop = 1, nozzle = 1, wait_time = [12,3,12], mode = 'dual')
#n2_bubbling.run()

# time.sleep(wait+5)

##### (N2 drying - nozzle 2 // 20 loops for drying at medium flow)
print('\n----\033[31mN2 drying\033[0m----')
n2_drying = controller.N2(loop = 1, nozzle = 2, wait_time = [12,3,12], mode = 'single')
n2_drying.run()

time.sleep(2)
power.state('OFF')
time.sleep(2)

power.state('ON')
time.sleep(2)

dispense_1d = controller.Dispense(nozzle=1, volume=500, wait_time=[0,3,12,3,0], motor_values=[-39000,80,-8530,80,39000], p = p_linear)
dispense_1d.run()

dispense_2d = controller.Dispense(nozzle=2, volume=500, wait_time=[0,3,12,3,0], motor_values=[-39000,80,-9230,80,39000], p = p_linear)
dispense_2d.run()

time.sleep(wait)
n2_drying.run()
##### (2. Rinsing)
## move_down / <<<LOOP start = suc / flush / equil_flush / suc = LOOP end>>> / move_up

# rinse = controller.Rinse(loop=2, wait_time=[16,12,3.5,12,12,16])
# rinse.run()
# time.sleep(30)

# rinse2 = controller.Rinse(loop=1, wait_time=[16,12,0,20,12,16]) # rinsing without flushing
# rinse2.run()
# time.sleep(wait-5)

power.state('OFF')
time.sleep(2)

print('Finished')
setup.disconnect()