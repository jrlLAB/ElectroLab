import controller
import time

# General setup
port = 'COM5'
baud_rate = 115200

setup = controller.Setup(port, baud_rate)
setup.connect()

wait = 10
move = controller.Motor()
power = controller.MainPower()

p1_default = [19.801938114061617,0.964367848880719,1.167139063529185e-05,-2.873709837738213e-09]
p2_default = [11.765533598083050, 0.994151183002726, -2.200584843815698e-05, 5.268389857671134e-09]
p_linear = [0,1,0,0]

# Main Power ON
print('\n----MAIN POWER ON----')
power.state('ON')
time.sleep(2)

# Homming
print('\n----NOZZLES HOMING----')
message_home2 = bytes('<homeDisp,0,0>', 'UTF-8')
move.send(message_home2)
time.sleep(wait+10)

print('\n----GANTRY HOMING----')
message_home1 = bytes('<homeGantry,0,0>', 'UTF-8')
move.send(message_home1)
time.sleep(wait+5)

print('\n----Moving to cell 4 (dummy)----')
pos = controller.Position_in_cell(4)
pos.run()
time.sleep(wait+5)

print('\n----Disp. 1 removing dead volume----')
dispense_1 = controller.Dispense(nozzle=1, volume=300, wait_time=[0,3,12,3,0], motor_values=[-39000,80,-8530,80,39000])
#dispense_1.run()
print('\n----Disp. 2 removing dead volume----')
dispense_2 = controller.Dispense(nozzle=2, volume=300, wait_time=[0,3,12,3,0], motor_values=[-39000,80,-9040,80,39000])
dispense_2.run()

print('\n----Moving to cell 2----')
pos = controller.Position_in_cell(2)
pos.run()
time.sleep(wait+5)


# vol_list = [100,100,100,150,150,150,300,300,300,500,500,500,750,750,750,1000,1000,1000]

vol_list = [250,250, 500, 500, 750,750,1000,1000]
disp1_cutoff = 670
disp2_cutoff = 780

time.sleep(5)

i_num = 1
print('\n----Dispense in cell 2 from Nozzle 2----')

time.sleep(13)

for x in vol_list:

    print(f'\n----Dispensing \033[31mNo. {i_num}\033[0m----')

    if x < disp2_cutoff:
        dispense_2d = controller.Dispense(nozzle=2, volume=x, wait_time=[0,3,12,3,0], motor_values=[-39000,80,-9040,80,39000], p = p2_default)
        print(f'From nozzle 2, dispensing \033[31m{x} \033[0muL  \n')
        dispense_2d.run()
    else:
        dispense_2d = controller.Dispense(nozzle=2, volume=x, wait_time=[0,3,12,3,0], motor_values=[-39000,80,-9040,80,39000], p = p_linear)
        print(f'From nozzle 2, dispensing \033[33m{x} \033[0muL  \n')
        dispense_2d.run()
    time.sleep(13)

    i_num += 1

# Main Power OFF
print('\n----MAIN POWER OFF----')
power.state('OFF')
time.sleep(2)

print('Finished')
setup.disconnect()

### <POWER,1,0>
### <PUMP1,1000,45000>
### <PUMP2,1000,45000>