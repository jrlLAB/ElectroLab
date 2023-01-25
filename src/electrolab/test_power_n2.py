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

# Power setup
power = controller.MainPower()

# Main Power ON
print('\n----MAIN POWER ON----')
power.state('ON')
time.sleep(2)

# Homming
print('\n----GANTRY HOMING----')
message_home1 = bytes('<homeGantry,0,0>', 'UTF-8')
move.send(message_home1)
time.sleep(wait+5)

# Main Power OFF
print('\n----MAIN POWER OFF----')
power.state('OFF')
time.sleep(2)

print('Doing Electrochemistry')
time.sleep(5)

# Main Power ON
print('\n----MAIN POWER ON----')
power.state('ON')
time.sleep(2)

## n2 test
# n2_bubbling = controller.N2(nozzle = 1, wait_time=[7,20,7])
# n2_bubbling.run()
# n2_drying = controller.N2(nozzle = 2, wait_time=[7,20,7])
# n2_drying.run()

# Main Power OFF
print('\n----MAIN POWER OFF----')
power.state('OFF')
time.sleep(2)

print('Finished')
setup.disconnect()