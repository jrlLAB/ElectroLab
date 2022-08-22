import controller
import time

wait = 10

# General setup
port = '/dev/ttyACM0'
baud_rate = 115200
controller.Setup(port, baud_rate)

controller.Position_in_cell(1).run()
time.sleep(wait)

dispense = controller.Dispense(nozzle=2,wait_time=[5,5,5,5])
dispense.run()

rinse = controller.Rinse(wait_time=[5,5,5,5,5])
rinse.run()
time.sleep(wait)

dry = controller.Dry(wait_time=[5,40,5])
dry.run()

controller.Position_in_cell(0).run()
time.sleep(wait)

controller.change_dispenser_nozzle(controller.nozzle_n,1)
time.sleep(wait)

motor = controller.Motor()
motor.send(b'<X,1000,28000>')

print('Finished')