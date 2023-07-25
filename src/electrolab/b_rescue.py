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
time.sleep(5)

# Homming
print("\n----NOZZLES HOMING----")
message_home2 = bytes("<homeDisp,0,0>", "UTF-8")
move.send(message_home2)
time.sleep(wait + 12)

print("\n----GANTRY HOMING----")
message_home1 = bytes("<homeGantry,0,0>", "UTF-8")
move.send(message_home1)
time.sleep(wait + 7)

######## Move to the cell being used for the failed test #############
print("\n----Moving to cell 2----")
pos = controller.Position_in_cell(2)  ### Change it to 2 or 3 ###
pos.run()
time.sleep(wait + 5)

### Initial Electrode Rinsing #################################################################
## "wait_time" in Rinse function (0 will skip the step, and below is the sequence)
## (1) Down / [LOOP start [ (2) suction / (3) flush / (4) suction] LOOP end] / (5) Up
## = [16, 12, 15, 12, 16]
rinse = controller.Rinse(
    loop=3, wait_time=[16, 12, 15, 12, 16]
)  # change the number of loops
rinse.run()
time.sleep(5)

### Electrode strong rinsing / bubbling / drying (SR) ###############################################
# (SR1) Filling reservoir with solvent
print("\n----\033[31m Filling reservoir with solvent \033[0m----")
filling_only = controller.Rinse(loop=1, wait_time=[16, 0, 15, 0, 16])
filling_only.run()

message_move1_back = bytes("<X,1000,-800>", "UTF-8")  # -870
move.send(message_move1_back)
time.sleep(10)

# (SR2) Argon bubbling
print("\n----\033[31mN2 bubbling\033[0m----")
n2_bubbling = controller.N2(loop=1, nozzle=2, wait_time=[12, 3, 12], mode="dual")
n2_bubbling.run()
time.sleep(7)

# (SR3) Suction only
suction_only = controller.Rinse(loop=1, wait_time=[16, 12, 0, 0, 16])
suction_only.run()
time.sleep(7)

# (SR4) Argon drying
print("\n----\033[31mN2 drying\033[0m----")
n2_drying = controller.N2(loop=1, nozzle=1, wait_time=[12, 3, 12], mode="single")
n2_drying.run()
time.sleep(10)

### Main Power OFF ##################################################################################

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
