import controller
import time
import datetime

start_time = time.time()

####define com ports for controller and baudrate (keep at 115200)
port = "COM5"
baud_rate = 115200

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
time.sleep(5)

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

######## Filling a flushing tube ######################################
print("\n----Flushing tube filling ----")
message_f4 = bytes(
    "<PUMP4,1000,25000>", "UTF-8"
)  # change the value if needed (SPEEDS, STEPS)
move.send(message_f4)
time.sleep(60)

######## Filling tube in dispenser 1 and 2 ######################################
print("\n----Disp. nozzle 1 & 2 initialization ----")

dispense_fill_1 = controller.Dispense(
    nozzle=1,
    volume=3300,
    speed=8000,
    wait_time=[70, 3, 0, 3, 0],
    motor_values=[-9000, 20, -2755, 20, 9000],
    p=p_linear,
)
dispense_fill_1.run()

dispense_fill_2 = controller.Dispense(
    nozzle=2,
    volume=3300,
    speed=8000,
    wait_time=[70, 3, 0, 3, 0],
    motor_values=[-9000, 20, -2755, 20, 9000],
    p=p_linear,
)
dispense_fill_2.run()

# Dummy cell suction
suction_only = controller.Rinse_dummy(loop=1, wait_time=[16, 12, 0, 0, 16])
suction_only.run()
time.sleep(5)

### Main Power OFF #################################################################
print("\n----MAIN POWER OFF----")
power.state("OFF")
time.sleep(5)

print("Finished")
setup.disconnect()

print("\n----\033[31m Print the total time duration \033[0m----")
end_time = time.time()
total_time = end_time - start_time
total_time_list = str(datetime.timedelta(seconds=total_time)).split(".")
print(total_time_list[0])  # Hrs:Mins:Secs format
