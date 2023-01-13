import controller
import time

port = 'COM3'
baud_rate = 115200

setup = controller.Setup(port, baud_rate)
setup.connect()

# controller.Setup(port, baud_rate)

power = controller.MainPower()
power.state('ON')
time.sleep(2)

power.state('OFF')
time.sleep(2)

power.state('ON')
time.sleep(2)

# setup.disconnect()
