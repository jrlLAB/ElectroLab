import serial
import time
import numpy as np

# Global variables
port_ = 'XXX'
baudRate = 123
ser = 0
state = 2 # Nozzle state (1: dispensing, 2: rinsing, 3: drying)
nozzle_n = 1 # dispenser nozzle number
position = 0 # Head position, 0: home, 1: cell 1, 2: cell2, etc
move_speed = 1000 # Movement speed
dx0 = 4450 # dx for the home position, [230116] 4350
dy0 = 2800 # [220830] newly added
dx = 2000
dy = 4000
head_12 = np.array([1920, 400]) # [230113]
head_23 = np.array([-1650, -1140]) # [230209] [-1740, -1140] & [-1520, -1140]
head_13 = np.array([-600, -680]) # [230113] [100, -680]
nozzle12 = np.array([-280, 400]) # [230113]

# Nitrogen nozzle global variables:
nozzle_n2_n = 1 # nitrogen-blowing nozzle number (1: drying, 2: bubbling)
nozzle12_n2 = np.array([870, 0])
head_23_n2 = np.array([-1680, -1140]) # [230209] [-1520, -1140]
head_13_n2 = np.array([-100, -680])  # [230125] [100, -680]

class Setup:
    '''
        - Here, test connection
    '''
    def __init__(self, port, baud_rate=baudRate, speed=move_speed):
        global port_
        port_ = port
        global baudRate
        baudRate = baud_rate
        global move_speed
        move_speed = speed
        print('----------')
        print('Port: ', port_)
        print('baud_rate: ', baudRate)
        print('Movement speed: ', move_speed)
        print('----------')

    def connect(self):
        global ser
        ser = serial.Serial(port_, baudRate)
        #print(ser.readline)
        
    def disconnect(self):
        ser.close()
        

class Motor:
    '''
        This and the Serial class are the same. This needs to be replaced
        with Serial throughout the code
    '''
    def __init__(self):
        pass

    def send(self, message):
        #ser = serial.Serial(port_, baudRate)
        #print(ser.readline())
        #print('Executing', message)
        time.sleep(1)
        ser.write(message)
        #ser.readline()
        #ser.readline()
        #ser.readline()
        #ser.close()

class Serial:
    def __init__(self):
        pass

    def send(self, message):
        #global ser
        #ser = serial.Serial(port_, baudRate)
        #print(ser.readline())
        #print('Executing', message)\
        time.sleep(1)
        ser.write(message)
        #ser.readline()
        #ser.readline()
        #ser.readline()
        #ser.close()
        

class MainPower(Serial):
    '''
        Sends command to the Relay to turn on or off the main power of the elab
    '''
    def __init__(self):
        pass

    def state(self, state):
        if state == 'ON':
            state = 1 
            print('ElectroLab ON')
        else:
            state = 0
            print('ElectroLab OFF')
        message = bytes('<POWER,' + str(int(state)) + ',0>', 'UTF-8')
        #print(message)
        self.send(message)


class Move(Motor):
    '''
    '''
    def __init__(self, pos1, pos2):
        Motor.__init__(self)
        self.pos1 = pos1
        self.pos2 = pos2

    def run(self):
        global move_speed
        route = self.pos1 + self.pos2
        messageX = '<X, ' + str(move_speed) + ', ' + str(route[0]) + '>'
        messageY = '<Y, ' + str(move_speed) + ', ' + str(route[1]) + '>'
        message = bytes(messageX + messageY, 'UTF-8')
        self.send(message)


class Move_head(Move):
    '''
        Cells xy:
        02, 12, 22, 32
        01, 11, 21, 31
        00, 10, 20, 30
    '''
    def __init__(self, cellA, cellB, wait_time=1):
        self.wait_time = wait_time
        global dx
        global dy
        global dx0
        global dy0 # [220830] newly added
        offset = 0
        cellA = str(cellA)
        cellB = str(cellB)
        if len(cellA) == 1:
            cellA = '0' + str(cellA)
        if len(cellB) == 1:
            cellB = '0' + str(cellB)
        xA = cellA[0]
        yA = cellA[1]
        xB = cellB[0]
        yB = cellB[1]

        route = np.array([int(xB)-int(xA), int(yB)-int(yA)]) \
                *np.array([dx,dy])
        if xA == '0':
            route[0] = route[0] + dx0 - dx
            route[1] = route[1] + dy0 - dy # [220830] newly added
        elif xB == '0':
            route[0] = route[0] - dx0 + dx
            route[1] = route[1] - dy0 + dy # [220830] newly added

        messageX = '<X, ' + str(move_speed) + ', ' + str(route[0]) + '>'
        messageY = '<Y, ' + str(move_speed) + ', ' + str(route[1]) + '>'
        self.message = bytes(messageX + messageY, 'UTF-8')

    def run(self):
        print('Positioning head')
        self.send(self.message)
        time.sleep(self.wait_time)
        print(self.message)

      
class Position_in_cell:
    '''
        This positions the rinsing head into the cell
    '''

    def __init__(self, cell, wait_time=1):
        global position # This knows what cell we are now
        self.cell = cell
        cellA = parse_cell(position)
        cellB = parse_cell(self.cell)
        if isinstance(cellB, str):
            raise Exception(cellB)
        else:
            self.move = Move_head(cellA, cellB, wait_time)

    def run(self):
        global position
        print('\nMoving to cell', self.cell)
        self.move.run()
        position = self.cell
        print(position)

def parse_cell(cell):
    if cell == 0:
        return 0
    elif cell == 1:
        return 11
    elif cell == 2:
        return 21
    elif cell == 3:
        return 31
    elif cell == 4:
        return 12
    elif cell == 5:
        return 22
    elif cell == 6:
        return 32
    else:
        return 'Cell number out of range (1-6)'



class Nozzle_change(Motor):
    '''
        state1: curent state
        state2: new state
    '''
    def __init__(self, state1, state2, wait_time=3):
        Motor.__init__(self)
        global head_12
        global head_23
        global head_13
        global move_speed
        global state
        self.wait_time = wait_time
        coordinates = np.array([0,0])
        state = state2
        print(state)
        print('Changing nozzle')
        if state1 == 1 and state2 == 2:
            coordinates = head_12
        elif state1 == 2 and state2 == 1:
            coordinates = -head_12
        elif state1 == 2 and state2 == 3:
            coordinates = head_23
        elif state1 == 3 and state2 == 2:
            coordinates = -head_23
        elif state1 == 1 and state2 == 3:
            coordinates = head_13
            print('Dry?')
        elif state1 == 3 and state2 == 1:
            coordinates = -head_13
        elif state1 == state2:
            print('Nozzle remained in the same position')
            state = state1
        else:
            print('Wrong coordinates for Nozzle_change')
            state = state1

        messageX = '<X, ' + str(move_speed) + ', ' + str(coordinates[0]) + '>'
        messageY = '<Y, ' + str(move_speed) + ', ' + str(coordinates[1]) + '>'
        self.message = bytes(messageX + messageY, 'UTF-8')
        #self.run()

    def run(self):
        print('Sending message')
        self.send(self.message)
        time.sleep(self.wait_time)


class Dispense(Motor):
    '''
        User can specify the volume to dispense in uL. The calibrated motor_values
        for the dispense operation is -9100, if a different value is needed
        the class will override the volume and set the manual motor value directly

        Pending: update wait_time according to volume
    '''
    def __init__(self, nozzle=1, volume=1000, wait_time=[47,3,0,0,0], speed=1000, 
                 motor_values=[-39000,80,-8530,80,39000], 
                 p=[19.801938114061617,0.964367848880719,1.167139063529185e-05,
                 -2.873709837738213e-09]):
        #global state # This is the general state
        global nozzle_n
        self.nozzle = nozzle
        self.wait_time = wait_time
        self.speed = speed
        self.motor_values = motor_values
        Motor.__init__(self)

        self.vol_correction(volume, p) # Corrected volume
        self.state = 1 # This is the internal state

    def vol_correction(self, volume, p=[0,0,0,0]):
        '''
            We assume the fitting is a cubic polynomial
        '''
        vol = p[0] + p[1]*volume + p[2]*volume**2 + p[3]*volume**3
        # Calibrated value to dispense 1 mL with a movement of -9100 by default
        slope = self.motor_values[2]/1000
        self.motor_values[2] = int(vol*slope)
        self.wait_time[0] = 0
        self.wait_time[2] = abs(slope*vol*11/(9.1*1000))

    def run(self):
        '''
            wait_time = [1,0,4,0]
            each number is the waiting time in s
            if 0 then that command is not executed
        '''
        #global state
        speed = str(self.speed)
        change_dispenser_nozzle(nozzle_n, self.nozzle, wait_time=3)
        if nozzle_n == 1:
            initialization = '<PUMP1, ' + speed + ', ' + \
                             str(self.motor_values[0]) +'>'
            remove_drip = '<PUMP1, ' + speed + ', ' + \
                          str(self.motor_values[1]) + '>'
            dispense = '<PUMP1, ' + speed + ', ' + \
                       str(self.motor_values[2]) + '>'
            remove_drip2 = '<PUMP1, ' + speed + ', ' + \
                          str(self.motor_values[3]) + '>'
            idle = '<PUMP1, '+ speed + ', ' + \
                   str(self.motor_values[4]) + '>'
        elif nozzle_n == 2:
            initialization = '<PUMP2, ' + speed + ', ' + \
                             str(self.motor_values[0]) +'>'
            remove_drip = '<PUMP2, ' + speed + ', ' + \
                          str(self.motor_values[1]) + '>'
            dispense = '<PUMP2, ' + speed + ', ' + \
                       str(self.motor_values[2]) + '>'
            remove_drip2 = '<PUMP2, ' + speed + ', ' + \
                          str(self.motor_values[3]) + '>'
            idle = '<PUMP2, '+ speed + ', ' + \
                   str(self.motor_values[4]) + '>'

        initialization = bytes(initialization, 'UTF-8')
        remove_drip = bytes(remove_drip, 'UTF-8')
        remove_drip2 = bytes(remove_drip2, 'UTF-8')
        dispense = bytes(dispense, 'UTF-8')
        idle = bytes(idle, 'UTF-8')

        change = Nozzle_change(state, self.state)
        change.run()
        print('Dispensing started')
        if self.wait_time[0]:
            self.send(initialization)
            time.sleep(self.wait_time[0])
        if self.wait_time[1]:
            self.send(remove_drip)
            time.sleep(self.wait_time[1])
        if self.wait_time[2]:
            self.send(dispense)
            time.sleep(self.wait_time[2])
        if self.wait_time[3]:
            self.send(remove_drip2)
            time.sleep(self.wait_time[3])
        if self.wait_time[4]:
            self.send(idle)
            time.sleep(self.wait_time[4])
        print('Dispensing finished')
        #state = self.state

        change_dispenser_nozzle(nozzle_n, 1, wait_time=3)


class Rinse(Motor):
    def __init__(self, loop=1, wait_time=[16,12,3.5,12,12,16]): # [221206] tune 2 [16,12,3,10,12,16]
        #global state
        self.wait_time = wait_time
        self.loop = loop
        Motor.__init__(self)
        self.state = 2

    def run(self):
        #global state
        move_down = b'<ZFLUSH, 100, +69300>' # [230116] +69200
        move_up = b'<ZFLUSH, 100, -69300>'
        flush = b'<DC4, 90, 2300>' # [221206] tune 80, [230116] 80, 5000 (medium), 65, 2700 (small)
        equil_flush = b'<DC5, 255, 6000>'
        suc = b'<DC2, 210, 15000>' # [230209] 20000

        change = Nozzle_change(state, self.state)
        change.run()
        print('Rinsing started')
        if self.wait_time[0]:
            self.send(move_down) 
            time.sleep(self.wait_time[0])
        for x in range(self.loop):
            if self.wait_time[1]:
                self.send(suc)
                time.sleep(self.wait_time[1])
            if self.wait_time[2]:
                self.send(flush)
                time.sleep(self.wait_time[2])
            if self.wait_time[3]:
                self.send(equil_flush)
                time.sleep(self.wait_time[3])
            if self.wait_time[4]:
                self.send(suc)
                time.sleep(self.wait_time[4])
        if self.wait_time[5]:
            self.send(move_up)
            time.sleep(self.wait_time[5]) # [220830] newly added
        print('Rinsing finished')
        #state = self.state

        
class Dry(Motor):
    def __init__(self, wait_time=[7,20,7]): # [221206] from [0,0,0]
        #global state
        self.wait_time = wait_time
        Motor.__init__(self)
        self.state = 3

    def run(self):
        #global state
        move_down = b'<ZAIRDRY, 100, +30000>'
        blast = b'<DC3, 255, 30000>' # 30000
        move_up = b'<ZAIRDRY, 100, -30000>'

        print(state)
        change = Nozzle_change(state, self.state)
        change.run()
        print(state)
        #print(self.state)
        print('Drying started')
        if self.wait_time[0]:
            self.send(move_down)
            time.sleep(self.wait_time[0])
        if self.wait_time[1]:
            self.send(blast)
            time.sleep(self.wait_time[1])
        if self.wait_time[2]:
            self.send(move_up)
            time.sleep(self.wait_time[2])
        print('Drying finished')
        #state = self.state


class N2(Motor):
    def __init__(self, nozzle=1, loop=1, wait_time=[12,3,12], mode='single'): # [221206] from [0,0,0]
        #global state
        self.nozzle = nozzle
        self.wait_time = wait_time
        self.loop = loop
        self.mode = mode
        Motor.__init__(self)
        self.state = 3

    def run(self):
        #global state
        #print(state)
        change = Nozzle_change(state, self.state)
        change.run()
        change_N2_nozzle(nozzle_n2_n, self.nozzle, wait_time=3)
        #print(state)
        if self.nozzle == 2:
            print('N2 bubbling started')
            if self.wait_time[0]:
                self.send(b'<ZAIRDRY, 100, +57000>') # med stream: 57000
                time.sleep(self.wait_time[0])
            if self.wait_time[1]:
                if self.mode == 'dual':
                    for x in range(self.loop):
                        self.send(b'<DC6, 255, 16000>')
                        time.sleep(5)
                        self.send(b'<DC3, 255, 8000>')
                        time.sleep(11)
                    time.sleep(self.wait_time[1])
                else: # By default, mode = 'single'
                    for x in range(self.loop):
                        self.send(b'<DC3, 255, 1000>')
                        time.sleep(1.2)
                    time.sleep(self.wait_time[1])
            if self.wait_time[2]:
                self.send(b'<ZAIRDRY, 100, -57000>')
                time.sleep(self.wait_time[2])
            print('N2 bubbling finished')

        elif self.nozzle == 1:
            print('N2 drying started')
            if self.wait_time[0]:
                self.send(b'<ZAIRDRY, 100, +55000>')
                time.sleep(self.wait_time[0])
            if self.wait_time[1]:
                for x in range(self.loop):
                    self.send(b'<DC6, 255, 6000>')
                    time.sleep(10) # 6 or 10 (strong, or med)
                time.sleep(self.wait_time[1])
            if self.wait_time[2]:
                self.send(b'<ZAIRDRY, 100, -55000>')
                time.sleep(self.wait_time[2])
            print('N2 drying finished')

        print(state)
        change = Nozzle_change(state, self.state)
        change.run()
        print(state)
        #print(self.state)
        # print('Drying started')
        # if self.wait_time[0]:
        #     self.send(b'<ZAIRDRY, 100, +30000>')
        #     time.sleep(self.wait_time[0])
        # if self.wait_time[1]:
        #     self.send(b'<DC3, 255, 3000>')
        #     time.sleep(self.wait_time[1])
        # if self.wait_time[2]:
        #     self.send(b'<ZAIRDRY, 100, -30000>')
        #     time.sleep(self.wait_time[2])
        # print('Drying finished')
        #state = self.state


def change_dispenser_nozzle(nozzle1, nozzle2, wait_time=1):
    global nozzle12
    global nozzle_n
    print('\nChanging dispensing nozzle from ' + str(nozzle1) + ' to ' + str(nozzle2))
    if nozzle1 == 1 and nozzle2 == 2:
        coordinates = nozzle12
        nozzle_n = 2
        messageX = '<X, ' + str(move_speed) + ', ' + str(coordinates[0]) + '>'
        messageY = '<Y, ' + str(move_speed) + ', ' + str(coordinates[1]) + '>'
        message = bytes(messageX + messageY, 'UTF-8')
    elif nozzle1 == 2 and nozzle2 ==1:
        coordinates = -nozzle12
        nozzle_n = 1
        messageX = '<X, ' + str(move_speed) + ', ' + str(coordinates[0]) + '>'
        messageY = '<Y, ' + str(move_speed) + ', ' + str(coordinates[1]) + '>'
        message = bytes(messageX + messageY, 'UTF-8')
    elif nozzle1 == nozzle2:
       print('Dispensing nozzle remained in the same position')
       coordinates = nozzle12
       message = bytes('', 'UTF-8')
    else:
        raise Exception('Select a correct dispensing nozzle number (1-2)')
    Motor().send(message)


def change_N2_nozzle(nozzle1, nozzle2, wait_time=1):
    global nozzle12_n2
    global nozzle_n2_n
    print('\nChanging N2 nozzle from ' + str(nozzle1) + ' to ' + str(nozzle2))
    if nozzle1 == 1 and nozzle2 == 2:
        coordinates = nozzle12_n2
        nozzle_n2_n = 2
        messageX = '<X, ' + str(move_speed) + ', ' + str(coordinates[0]) + '>'
        messageY = '<Y, ' + str(move_speed) + ', ' + str(coordinates[1]) + '>'
        message = bytes(messageX + messageY, 'UTF-8')
    elif nozzle1 == 2 and nozzle2 ==1:
        coordinates = -nozzle12_n2
        nozzle_n2_n = 1
        messageX = '<X, ' + str(move_speed) + ', ' + str(coordinates[0]) + '>'
        messageY = '<Y, ' + str(move_speed) + ', ' + str(coordinates[1]) + '>'
        message = bytes(messageX + messageY, 'UTF-8')
    elif nozzle1 == nozzle2:
       print('Dispensing nozzle remained in the same position')
       coordinates = nozzle12_n2
       message = bytes('', 'UTF-8')
    else:
        raise Exception('Select a correct dispensing nozzle number (1-2)')
    Motor().send(message)
