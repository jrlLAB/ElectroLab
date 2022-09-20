import controller
import time

wait = 10

# General setup
port = 'COM3'
baud_rate = 115200
controller.Setup(port, baud_rate)

controller.Position_in_cell(1).run()
time.sleep(wait)