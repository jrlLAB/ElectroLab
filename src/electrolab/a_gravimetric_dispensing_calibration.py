# Code used for the Gravimetric Dispensing Calibration
# Use this script after running "a_initialization.py"

import controller
import time

####define com ports for controller and baudrate (keep at 115200)
port = "COM5"
baud_rate = 115200

###setup controller
setup = controller.Setup(port, baud_rate)
setup.connect()

#################### Fluidics parameters ###########################
wait = 10
move = controller.Motor()
power = controller.MainPower()

# Parameters related to peristaltic pumps
p1_new = [
    13.712609063042798,
    0.977763871750637,
    4.104248850640944e-05,
    -4.143399187088928e-08,
]
p1_default = [
    19.801938114061617,
    0.964367848880719,
    1.167139063529185e-05,
    -2.873709837738213e-09,
]
p2_default = [
    11.765533598083050,
    0.994151183002726,
    -2.200584843815698e-05,
    5.268389857671134e-09,
]
p_linear = [0, 1, 0, 0]

########### start of script! #################################################

# Main Power ON
print("\n----MAIN POWER ON----")
power.state("ON")
time.sleep(2)

# Homming
print("\n----NOZZLES HOMING----")
message_home2 = bytes("<homeDisp,0,0>", "UTF-8")
move.send(message_home2)
time.sleep(wait + 10)

print("\n----GANTRY HOMING----")
message_home1 = bytes("<homeGantry,0,0>", "UTF-8")
move.send(message_home1)
time.sleep(wait + 5)

# Move to the dummy cell
print("\n----Moving to cell 4 (dummy)----")
pos = controller.Position_in_cell(4)
pos.run()
time.sleep(wait + 5)

# Dummy dispensing to remove trapped air bubbles in tubes
print("\n----Disp. 1 removing dead volume----")
dispense_1 = controller.Dispense(
    nozzle=1,
    volume=300,
    speed=8000,
    wait_time=[0, 3, 26.4, 3, 0],
    motor_values=[-9000, 20, -2755, 20, 9000],
    p=p_linear,
)
dispense_1.run()

# Move to the cell 1 (but you need to hold 1.5 mL Microcentrifuge tubes with snap cap, or vials)
print("\n----Moving to cell 1----")
pos = controller.Position_in_cell(1)
pos.run()
time.sleep(wait + 5)

disp1_cutoff = 600
disp2_cutoff = 600

# (Step 1) Calibaration : run the volume dispensing (100 to 750 uL) with n = 3,
#                         and estimate the cubic polynomial p_values for fitting

# vol_list = [100,100,100,200,200,200,300,300,300,500,500,500,750,750,750]
# p_current = p_linear


# (Step 2) Test : check the dispensing with non-linearly calibrated volume function

vol_list = [
    100,
    100,
    100,
    250,
    250,
    250,
    500,
    500,
    500,
    750,
    750,
    750,
    1000,
    1000,
    1000,
]
p1_new = [
    13.712609063042798,
    0.977763871750637,
    4.104248850640944e-05,
    -4.143399187088928e-08,
]
p_current = p1_new


time.sleep(5)

i_num = 1  # counting index
print("\n----Dispense in cell 2 from Nozzle 2----")

time.sleep(13)

### dispense solutions to the vials ##############################################
for x in vol_list:
    print(f"\n----Dispensing \033[31mNo. {i_num}\033[0m----")

    if x < disp2_cutoff:
        dispense_1d = controller.Dispense(
            nozzle=1,
            volume=x,
            speed=8000,
            wait_time=[0, 3, 26.4, 3, 0],
            motor_values=[-9000, 20, -2755, 20, 9000],
            p=p_current,
        )
        print(f"From nozzle 2, dispensing \033[31m{x} \033[0muL  \n")
        dispense_1d.run()
    else:
        dispense_1d = controller.Dispense(
            nozzle=1,
            volume=x,
            speed=8000,
            wait_time=[0, 3, 26.4, 3, 0],
            motor_values=[-9000, 20, -2755, 20, 9000],
            p=p_current,
        )
        print(f"From nozzle 2, dispensing \033[33m{x} \033[0muL  \n")
        dispense_1d.run()
    time.sleep(13)

    i_num += 1

### Main Power OFF #################################################################
print("\n----MAIN POWER OFF----")
power.state("OFF")
time.sleep(2)

print("Finished")
setup.disconnect()
