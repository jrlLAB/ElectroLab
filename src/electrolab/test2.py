import controller
import time

# General setup
port = 'COM3'
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

print('\n----Moving x=1000, y=1000----')
# Move positive
mes1 = bytes('<X,1000,1000><Y,1000,1000>', 'UTF-8')
move.send(mes1)
time.sleep(wait-5)

# Move negative
print('\n----Moving x=-1000, y=-1000]----')
mes2 = bytes('<X,1000,-1000><Y,1000,-1000>', 'UTF-8')
move.send(mes2)
time.sleep(wait-5)

print('\n----Moving to cell 1----')
pos = controller.Position_in_cell(1)
pos.run()
time.sleep(wait)

print('\n----Moving to cell 5----')
pos = controller.Position_in_cell(5)
pos.run()
time.sleep(wait)

print('\n----Moving to cell 1----')
pos = controller.Position_in_cell(1)
pos.run()
time.sleep(wait)

# Homming
print('\n----HOMMING----')
message_home = bytes('<homeGantry,0,0>', 'UTF-8')
move.send(message_home)
time.sleep(wait)

print('Finished')
setup.disconnect()
