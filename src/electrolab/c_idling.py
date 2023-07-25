import controller
import time
import datetime

start_time = time.time()

####define com ports for controller and baudrate (keep at 115200)
# port = '/dev/ttyACM0' # Linux
port = "COM5"  # Windows
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
time.sleep(2)

# Homming
print("\n----NOZZLES HOMING----")
message_home2 = bytes("<homeDisp,0,0>", "UTF-8")
move.send(message_home2)
time.sleep(wait + 12)

print("\n----GANTRY HOMING----")
message_home1 = bytes("<homeGantry,0,0>", "UTF-8")
move.send(message_home1)
time.sleep(wait + 5)

### Emptying dispensing & flushing tubes #################################################################
print("\n----Moving to cell 4 (dummy)----")
pos = controller.Position_in_cell(4)
pos.run()
time.sleep(wait + 5)

print("\n \033[33m Now emptying tubes filled with samples \033[0m \n")
message_n1 = bytes("<PUMP2,8000,9000>", "UTF-8")  # 9000
message_n2 = bytes("<PUMP3,8000,9500>", "UTF-8")  # 9500
message_f4 = bytes(
    "<PUMP4,1000,-30000>", "UTF-8"
)  # if needed, check the values and the sign

move.send(message_n1)
time.sleep(2)
move.send(message_n2)
time.sleep(2)
move.send(message_f4)
time.sleep(85)

print(
    "\n \033[33m Please change glass bottles (from dispensing to flushing ones) \033[0m \n"
)

### PRESS ENTER KEY to PROCEED
input("\033[31m Press ENTER key to proceed... \033[0m \n")

### Flushing dispensing tubes #################################################################
message_move1 = bytes("<X,1000,-1920>", "UTF-8")
message_move2 = bytes("<Y,1000,-50>", "UTF-8")
move.send(message_move1)
time.sleep(2)
move.send(message_move2)
time.sleep(2)

print("\n \033[33m Now flushing tubes with flushing solvents \033[0m \n")
message_f1 = bytes("<PUMP2,8000,-12000>", "UTF-8")
message_f2 = bytes("<PUMP3,8000,-12000>", "UTF-8")

move.send(message_f1)
time.sleep(2)
move.send(message_f2)

time.sleep(95)

### PRESS ENTER KEY to PROCEED
input("\n \033[31m Press ENTER key to proceed... \033[0m \n")

### Cleaning the dummy cell #################################################################
message_move1_back = bytes("<X,1000,1920>", "UTF-8")
message_move2_back = bytes("<Y,1000,50>", "UTF-8")
move.send(message_move1_back)
time.sleep(2)
move.send(message_move2_back)
time.sleep(2)

## "wait_time" in Rinse function (0 will skip the step, and below is the sequence)
## (1) Down / [LOOP start [ (2) suction / (3) flush (skipped) / (4) suction] LOOP end] / (5) Up
## = [16, 12, 0, 12, 16]
rinse = controller.Rinse_dummy(
    loop=1, wait_time=[16, 12, 0, 12, 16]
)  # change the number of loops
rinse.run()
time.sleep(5)

### Emptying dispensing tubes #################################################################
print("\n \033[33m Now emptying tubes filled with flushing solvents \033[0m \n")
message_n1 = bytes("<PUMP2,8000,9000>", "UTF-8")
message_n2 = bytes("<PUMP3,8000,9500>", "UTF-8")

move.send(message_n1)
time.sleep(2)
move.send(message_n2)
time.sleep(85)

### Main Power OFF ##################################################################################
print("\n----MAIN POWER OFF----")
power.state("OFF")
time.sleep(2)

print("Finished")
setup.disconnect()

print("\n----\033[31m Print the total time duration \033[0m----")
end_time = time.time()
total_time = end_time - start_time
total_time_list = str(datetime.timedelta(seconds=total_time)).split(".")
print(total_time_list[0])  # Hrs:Mins:Secs format
