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
time.sleep(wait+12)

print('\n----GANTRY HOMING----')
message_home1 = bytes('<homeGantry,0,0>', 'UTF-8')
move.send(message_home1)
time.sleep(wait+5)

# (1) Emptying tubes
message_n1 = bytes('<PUMP1,1000,45000>', 'UTF-8')
message_n2 = bytes('<PUMP2,1000,45000>', 'UTF-8')
move.send(message_n1)
time.sleep(2)
move.send(message_n2)
time.sleep(80)

print('\033[33m Change glass bottles (from dispensing to flushing ones) \033[0m \n')
input('\033[31m Press ENTER key to proceed... \033[0m \n')

# (2) Flushing tubes
print('\n----Moving to cell 5 (dummy)----')
pos = controller.Position_in_cell(5)
pos.run()
time.sleep(wait+5)

message_f1 = bytes('<PUMP1,1000,-50000>', 'UTF-8')
message_f2 = bytes('<PUMP2,1000,-50000>', 'UTF-8')
move.send(message_n1)
time.sleep(2)
move.send(message_n2)
time.sleep(80)

input('\033[31m Press ENTER key to proceed... \033[0m \n')

# (2) Emptying tubes
message_n1 = bytes('<PUMP1,1000,45000>', 'UTF-8')
message_n2 = bytes('<PUMP2,1000,45000>', 'UTF-8')
move.send(message_n1)
time.sleep(2)
move.send(message_n2)
time.sleep(80)

# Main Power OFF
print('\n----MAIN POWER OFF----')
power.state('OFF')
time.sleep(2)

print('Finished')
setup.disconnect()

### <POWER,1,0>
### <PUMP1,1000,45000>
### <PUMP2,1000,45000>