import controller
import time

wait = 10

# General setup
port = 'COM3'
baud_rate = 115200
controller.Setup(port, baud_rate)

dry = controller.Dry(wait_time=[5,40,5])
dry.run()