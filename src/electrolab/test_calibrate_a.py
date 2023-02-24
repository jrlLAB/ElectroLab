import controller
import time

# General setup
# port = '/dev/ttyACM0' # Linux
port = 'COM5' # Windows
baud_rate = 115200

setup = controller.Setup(port, baud_rate)
setup.connect()

wait = 10
move = controller.Motor()
power = controller.MainPower()

# Parameters related to peristaltic pumps
p1_default = [19.801938114061617,0.964367848880719,1.167139063529185e-05,-2.873709837738213e-09]
p2_default = [11.765533598083050, 0.994151183002726, -2.200584843815698e-05, 5.268389857671134e-09]
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

print('\n----Moving to cell 1----')
pos = controller.Position_in_cell(1)
pos.run()
time.sleep(wait)

# print('\n----Dispense in cell 1 from Nozzle 1 & 2----')
# dispense_1 = controller.Dispense(nozzle=1, volume=700, wait_time=[0,3,12,3,0], motor_values=[-39000,80,-8530,80,39000])
# dispense_1.run()
# time.sleep(10)

# dispense_2 = controller.Dispense(nozzle=2, volume=700, wait_time=[0,3,12,3,0], motor_values=[-39000,80,-9300,80,39000])
# dispense_2.run()
# time.sleep(10)

# ELECTROLYTES

# (1) dummy dispense
print('\n----Dummy dispensing----')
dispense_2d = controller.Dispense(nozzle=2, volume=500, wait_time=[0,3,12,3,0], motor_values=[-39000,80,-9040,80,39000], p = p_linear)
dispense_2d.run()
time.sleep(10)

# (2) real dispense
print('\n----Real dispensing (1st)----')
dispense_2 = controller.Dispense(nozzle=2, volume=1000, wait_time=[0,3,12,3,0], motor_values=[-39000,80,-9040,80,39000], p = p_linear)
dispense_2.run()
time.sleep(15)
print('\n----Real dispensing (2nd)----')
time.sleep(5)
dispense_2.run()
time.sleep(5)

# Main Power OFF
print('\n----MAIN POWER OFF----')
power.state('OFF')
time.sleep(2)

# <POWER,1,0>
# <PUMP1,1000,45000>
# <PUMP2,1000,45000>

# Homming
# print('\n----HOMMING----')
# message_home = bytes('<homeGantry,0,0>', 'UTF-8')
# move.send(message_home)
# time.sleep(wait)

print('Finished')
setup.disconnect()
