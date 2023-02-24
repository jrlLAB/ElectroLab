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

# [HOW TO USE THIS CODE] test or run simple routines (e.g. filling or emptying one tube)

# [CAUTION] While filling tubes with this code, you should put some containers
# below dispensing nozzles to receive dripping liquids.

# Main Power ON
print('\n----MAIN POWER ON----')
power.state('ON')
time.sleep(2)

# Homming
print('\n----NOZZLES HOMING----')
message_home2 = bytes('<homeDisp,0,0>', 'UTF-8')
# move.send(message_home2)
# time.sleep(wait+12)

print('\n----GANTRY HOMING----')
message_home1 = bytes('<homeGantry,0,0>', 'UTF-8')
# move.send(message_home1)
# time.sleep(wait+7)

# (1) Emptying tubes, when 45000 (filling, if -45000)
print('\n \033[33m Now emptying tubes filled with samples \033[0m \n')
# message_n1 = bytes('<PUMP1,1000,45000>', 'UTF-8')
message_n2 = bytes('<PUMP2,1000,45000>', 'UTF-8')
# move.send(message_n1)
# time.sleep(2)
move.send(message_n2)
time.sleep(60)

# Main Power OFF
print('\n----MAIN POWER OFF----')
power.state('OFF')
time.sleep(2)

print('Finished')
setup.disconnect()