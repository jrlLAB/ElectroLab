import controller
import numpy as np

# General setup
port = '/dev/ttyACM0'
baud_rate = 115200
controller.Setup(port, baud_rate)

# Positioning the head
move_head = controller.Move_head(11,32)
move_head.run()

# Operation setup
dispense = controller.Dispense(wait_time=[1,1,1,1])
rinse = controller.Rinse(wait_time=[1,1,1,1,1,1,1])
dry = controller.Dry(wait_time=[1,1,1])

# Execution
dispense.run()
#rinse.run()
#dry.run()
rinse.run()

move_head = controller.Move_head(32,00)
move_head.run()

