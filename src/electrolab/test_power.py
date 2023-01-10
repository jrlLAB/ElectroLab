import controller
import time

port = 'COM3'
baud_rate = 115200

controller.Setup(port, baud_rate)
# setup.connect()

# controller.Setup(port, baud_rate)

power = controller.MainPower()
power.state('ON')

time.sleep(5)

power.state('OFF')
time.sleep(5)

# setup.disconnect()
