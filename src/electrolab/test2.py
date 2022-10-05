import controller
import time
import serial

# General setup
port = '/dev/ttyACM0'
baud_rate = 115200
setup = controller.Setup(port, baud_rate)
setup.connect()

#ser = serial.Serial(port, baud_rate)

wait = 1

move = controller.Motor()

# Homming
message_home = bytes('<homeGantry,0,0>', 'UTF-8')
move.send(message_home)
time.sleep(wait)

pos = controller.Position_in_cell(1)
pos.run()
time.sleep(wait)

pos = controller.Position_in_cell(5)
pos.run()
time.sleep(wait)

pos = controller.Position_in_cell(1)
pos.run()
time.sleep(wait)


# Move positive
mes1 = bytes('<Y,1000,1000>', 'UTF-8')
move.send(mes1)
time.sleep(wait)

# Move negative
mes2 = bytes('<Y,1000,-1000>', 'UTF-8')
move.send(mes2)
time.sleep(wait)

setup.disconnect()
print('Finished')
