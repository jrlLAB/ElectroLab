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

power.state('OFF')

power.state('ON')

# Homming
print('\n----GANTRY HOMING----')
message_home1 = bytes('<homeGantry,0,0>', 'UTF-8')
move.send(message_home1)
time.sleep(wait+5)

power.state('OFF')

print('Doing Electrochemistry')
time.sleep(5)

power.state('ON')

## first, test turn on and off
#print('\n----MAIN POWER ON----')
#time.sleep(5)

print('\n----GANTRY HOMING----')
message_home1 = bytes('<homeGantry,0,0>', 'UTF-8')
move.send(message_home1)
time.sleep(wait+5)


power.state('OFF')


## n2 test
# n2_bubbling = controller.N2(nozzle = 1, wait_time=[7,20,7])
# n2_bubbling.run()
# n2_drying = controller.N2(nozzle = 2, wait_time=[7,20,7])
# n2_drying.run()
print('Finished')
setup.disconnect()