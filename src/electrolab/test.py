import controller

# General setup
port = '/dev/ttyACM0'
baud_rate = 115200
controller.Setup(port, baud_rate)

##### Positioning the head
controller.Position_in_cell(3).run()

##### Operation setup
dispense = controller.Dispense(nozzle=2,wait_time=[1,1,1,1])
rinse = controller.Rinse(wait_time=[1,1,1,1,1,1,1])
dry = controller.Dry(wait_time=[1,1,1])

##### Execution
dispense.run()
rinse.run()
dry.run()
rinse.run()

##### Return head to home and dispensing nozzle to 1
controller.Position_in_cell(0).run()
controller.change_dispenser_nozzle(controller.nozzle_n,1)