import controller
import time

# General setup
port = 'COM3'
baud_rate = 115200

setup = controller.Setup(port, baud_rate)
setup.connect()

wait = 10

move = controller.Motor()

p1_default = [19.801938114061617,0.964367848880719,1.167139063529185e-05,-2.873709837738213e-09]
p2_default = [19.751968491759097,0.952312160718057,3.235820687217786e-05,-1.557420164573522e-08]
p_linear = [0,1,0,0]

# Homming
print('\n----GANTRY HOMING----')
message_home1 = bytes('<homeGantry,0,0>', 'UTF-8')
move.send(message_home1)
time.sleep(wait+5)

print('\n----NOZZLES HOMING----')
message_home2 = bytes('<homeDisp,0,0>', 'UTF-8')
move.send(message_home2)
time.sleep(wait+10)

print('\n----Moving to cell 4 (dummy)----')
pos = controller.Position_in_cell(4)
pos.run()
time.sleep(wait+5)

# tube filling (commentize it if needed)
print('\n----Disp. 1 tube filling----')
dispense_fill_1 = controller.Dispense(nozzle=1, volume=4500, wait_time=[47,3,0,3,0], motor_values=[-39000,80,-8530,80,39000], p = [0,1,0,0])
dispense_fill_1.run()

print('\n----Disp. 2 tube filling----')
dispense_fill_2 = controller.Dispense(nozzle=2, volume=4500, wait_time=[47,3,0,3,0], motor_values=[-39000,80,-9230,80,39000], p = [0,1,0,0])
dispense_fill_2.run()
# tube filling (end)

print('\n----Disp. 1 removing dead volume----')
dispense_1 = controller.Dispense(nozzle=1, volume=300, wait_time=[0,3,12,3,0], motor_values=[-39000,80,-8530,80,39000])
dispense_1.run()
print('\n----Disp. 2 removing dead volume----')
dispense_2 = controller.Dispense(nozzle=2, volume=300, wait_time=[0,3,12,3,0], motor_values=[-39000,80,-9230,80,39000])
dispense_2.run()

print('\n----Moving to cell 2----')
pos = controller.Position_in_cell(2)
pos.run()
time.sleep(wait+5)


print('\n----Dispense in cell 2 from Nozzle 1----')

vol_list = [100, 150, 200, 300, 400, 500, 600, 700, 800, 1000]
disp1_cutoff = 670
disp2_cutoff = 580

time.sleep(10)
for x in vol_list:
    if x < disp1_cutoff:
        dispense_1d = controller.Dispense(nozzle=1, volume=x, wait_time=[0,3,12,3,0], motor_values=[-39000,80,-8530,80,39000], p = p1_default)
        print(f'From nozzle 1, dispensing \033[31m{x} \033[0muL  \n')
        dispense_1d.run()
    else:
        dispense_1d = controller.Dispense(nozzle=1, volume=x, wait_time=[0,3,12,3,0], motor_values=[-39000,80,-8530,80,39000], p = p_linear)
        print(f'From nozzle 1, dispensing \033[33m{x} \033[0muL  \n')
        dispense_1d.run()
    time.sleep(10)

time.sleep(10)
for x in vol_list:
    if x < disp2_cutoff:
        dispense_2d = controller.Dispense(nozzle=2, volume=x, wait_time=[0,3,12,3,0], motor_values=[-39000,80,-9230,80,39000], p = p2_default)
        print(f'From nozzle 2, dispensing \033[31m{x} \033[0muL  \n')
        dispense_2d.run()
    else:
        dispense_2d = controller.Dispense(nozzle=2, volume=x, wait_time=[0,3,12,3,0], motor_values=[-39000,80,-9230,80,39000], p = p_linear)
        print(f'From nozzle 2, dispensing \033[33m{x} \033[0muL  \n')
        dispense_2d.run()
    time.sleep(10)

# <PUMP1,1000,45000>
# <PUMP2,1000,45000>

print('Finished')
setup.disconnect()