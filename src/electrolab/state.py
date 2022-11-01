import controller
import time

# General setup
port = '/dev/ttyACM0' # Linux
#port = 'COM3' # Windows
baud_rate = 115200

setup = controller.Setup(port, baud_rate)
setup.connect()

wait = 10

move = controller.Motor()

# Homming
print('\n----HOMMING----')
message_home = bytes('<homeGantry,0,0>', 'UTF-8')
move.send(message_home)
time.sleep(wait)

print('\n----Moving to cell 1----')
pos = controller.Position_in_cell(1)
pos.run()
time.sleep(wait)

#nozzle = controller.Nozzle_change(2,1,10)
#nozzle.run()

print('\n----Dispense in cell 1 from Nozzle 1----')
dispense = controller.Dispense(nozzle=1, volume=500)
dispense.run()

#print('\n----Rinse cell 1----')
#rinse = controller.Rinse()
#rinse.run()

print('\n----Dry----')
dry = controller.Dry(wait_time=[7,25,7])
dry.run()

print('\n----Dispense in cell 1 from Nozzle 2----')
dispense = controller.Dispense(nozzle=2, volume=500)
dispense.run()

#print('\n----Rinse cell 1----')
#rinse = controller.Rinse()
#rinse.run()

print('\n----Dry----')
dry = controller.Dry(wait_time=[7,25,7])
dry.run()


print('Finished')
setup.disconnect()
