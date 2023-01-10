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

## first, test turn on and off
print('\n----MAIN POWER ON----')
message_mp_on = bytes('<POWER,1,0>', 'UTF-8') # turn on the relay
message_mp_off = bytes('<POWER,0,0>', 'UTF-8') # turn off the relay

time.sleep(5)

print('OFF')
move.send(message_mp_off)
time.sleep(wait)

print('ON')
move.send(message_mp_on)
time.sleep(wait)

## n2 test
# n2_bubbling = controller.N2(nozzle = 1, wait_time=[7,20,7])
# n2_bubbling.run()

# n2_drying = controller.N2(nozzle = 2, wait_time=[7,20,7])
# n2_drying.run()

print('Finished')
setup.disconnect()