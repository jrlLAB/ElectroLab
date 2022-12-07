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

# Homming
print('\n----HOMMING----')
message_home = bytes('<homeGantry,0,0>', 'UTF-8')
move.send(message_home)
time.sleep(wait)

print('\n----Moving to cell 4 (dummy)----')
pos = controller.Position_in_cell(4)
pos.run()
time.sleep(wait)

print('\n----Dispense in cell 1 from Nozzle 1 & 2----')
dispense_1 = controller.Dispense(nozzle=1, volume=700, wait_time=[0,3,12,3,0], motor_values=[-39000,80,-8530,80,39000])
dispense_1.run()
time.sleep(10)

dispense_2 = controller.Dispense(nozzle=2, volume=700, wait_time=[0,3,12,3,0], motor_values=[-39000,80,-9300,80,39000])
dispense_2.run()
time.sleep(10)


# <PUMP1,1000,45000>
# <PUMP2,1000,45000>

# Homming
# print('\n----HOMMING----')
# message_home = bytes('<homeGantry,0,0>', 'UTF-8')
# move.send(message_home)
# time.sleep(wait)

print('Finished')
setup.disconnect()
