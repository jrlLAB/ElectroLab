import controller
import time

port = 'COM3'
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
time.sleep(wait+10)

print('\n----GANTRY HOMING----')
message_home1 = bytes('<homeGantry,0,0>', 'UTF-8')
move.send(message_home1)
time.sleep(wait+5)

# Move to the dummy cell
print('\n----Moving to cell 4 (dummy)----')
pos = controller.Position_in_cell(4)
pos.run()
time.sleep(wait+5)

##### (1. Filling tube in dispenser 1)
## init / remove_drip / dispense / remove_drip2 / idle

print('\n----Disp. nozzle 1 & 2 initialization ----')

dispense_fill_1 = controller.Dispense(nozzle=1, volume=200, wait_time=[47,3,0,3,0], motor_values=[-39000,80,-8530,80,39000], p = p_linear)
dispense_fill_1.run()

dispense_fill_2 = controller.Dispense(nozzle=2, volume=1500, wait_time=[47,3,0,3,0], motor_values=[-39000,80,-9230,80,39000], p = p_linear)
dispense_fill_2.run()

dispense_1 = controller.Dispense(nozzle=1, volume=300, wait_time=[0,3,12,3,0], motor_values=[-39000,80,-8530,80,39000], p = p_linear)
#dispense_1.run()

dispense_2 = controller.Dispense(nozzle=2, volume=300, wait_time=[0,3,12,3,0], motor_values=[-39000,80,-9230,80,39000], p = p_linear)
#dispense_2.run()

##### (4. Move back to Cell 1)
print('\n----Moving to cell 1----')
pos = controller.Position_in_cell(1)
pos.run()
time.sleep(wait)

# Main Power OFF
print('\n----MAIN POWER OFF----')
power.state('OFF')
time.sleep(2)

print('Finished')
setup.disconnect()


### <POWER,1,0>
### <PUMP1,1000,45000>
### <PUMP2,1000,45000>