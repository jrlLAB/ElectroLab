import controller
import time

wait = 10

# General setup
port = 'COM3'
baud_rate = 115200
controller.Setup(port, baud_rate)

rinse = controller.Rinse(wait_time=[3,2,3,10,10,3])
rinse.run()

time.sleep(3)