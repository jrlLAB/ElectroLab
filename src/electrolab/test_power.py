import controller
import time

port = '/dev/ttyACM0'
baud_rate = 115200

controller.Setup(port, baud_rate)
power = controller.MainPower()
power.state('ON')

time.sleep(5)

power.state('OFF')
