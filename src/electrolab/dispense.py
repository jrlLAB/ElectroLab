import controller
import time

# General setup
port = '/dev/ttyACM0' # Linux
#port = 'COM3' # Windows
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

print('\n----Moving to cell 1----')
pos = controller.Position_in_cell(1)
pos.run()
time.sleep(wait)

print('\n----Initialization in cell 1----')
dispense = controller.Dispense(nozzle=1)
dispense.run()

print('\n----Moving to cell 5----')
pos = controller.Position_in_cell(5)
pos.run()
time.sleep(wait)

print('\n----Dispense in cell 5----')
dispense = controller.Dispense(nozzle=1, volume=500)
dispense.run()


# Homming
print('\n----HOMMING----')
message_home = bytes('<homeGantry,0,0>', 'UTF-8')
move.send(message_home)
time.sleep(wait)

print('Finished')
setup.disconnect()
