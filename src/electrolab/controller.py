import serial
import time
import numpy as np

# Global variables
port_ = 'XXX'
baudRate = 123
state = 1 # Nozzle state (1: dispensing, 2: rinsing, 3: drying)
nozzle_n = 1 # dispenser nozzle number
position = 0 # Head position, 0: home, 1: cell 1, 2: cell2, etc
move_speed = 1000 # Movement speed
dx0 = 4400 # dx for the home position
dy0 = 2800 # [220830] newly added
dx = 2000
dy = 4000 # [220830] previsouly 2800, but now 4000
head_12 = np.array([2160, 150])
head_23 = np.array([-1740, -1140])
head_13 = np.array([420, -990])
nozzle12 = np.array([-350, 140]) # [220830] previsouly [-50, 400], but now [-350, 140]

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
        

class Motor:
    def __init__(self):
        pass

    def send(self, message):
        ser = serial.Serial(port_, baudRate)
        print('Executing', message)
        ser.write(message)
        ser.close()
        

class Move(Motor):
    '''
        This class may be redundant when used in Move_head
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
    '''
    def __init__(self, state1, state2, wait_time=1):
        Motor.__init__(self)
        global head_12
        global head_23
        global head_13
        global move_speed
        self.wait_time = wait_time
        coordinates = np.array([0,0])
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
        elif state1 == 3 and state2 == 1:
            coordinates = -head_13
        elif state1 == state2:
            print('Nozzle remained in the same position')
        else:
            print('Wrong coordinates for Nozzle_change')

        messageX = '<X, ' + str(move_speed) + ', ' + str(coordinates[0]) + '>'
        messageY = '<Y, ' + str(move_speed) + ', ' + str(coordinates[1]) + '>'
        self.message = bytes(messageX + messageY, 'UTF-8')
        self.run()

    def run(self):
        self.send(self.message)
        time.sleep(self.wait_time)


def change_dispenser_nozzle(nozzle1, nozzle2, wait_time=1):
    global nozzle12
    global nozzle_n
    print('\nChanging dispensing nozzle from ' + str(nozzle1) + ' to ' + str(nozzle2))
    if nozzle1 == 1 and nozzle2 == 2:
        coordinates = nozzle12
        nozzle_n = 2
    elif nozzle1 == 2 and nozzle2 ==1:
        coordinates = -nozzle12
        nozzle_n = 1
    elif nozzle1 == nozzle2:
       print('Dispensing nozzle remained in the same position')
    else:
        raise Exception('Select a correct dispensing nozzle number (1-2)')
    

class Dispense(Motor):
    '''
    '''
    def __init__(self, nozzle=1, wait_time=[0,0,0,0], speed=1000, 
                 motor_values=[100,-100,100,100]):
        global state # This is the general state
        global nozzle_n
        self.nozzle = nozzle
        self.wait_time = wait_time
        self.speed = speed
        self.motor_values = motor_values
        Motor.__init__(self)
        self.state = 1 # This is the internal state

    def run(self):
        '''
            wait_time = [1,0,4,0]
            each number is the waiting time in s
            if 0 then that command is not executed
        '''
        global state
        speed = str(self.speed)
        change_dispenser_nozzle(nozzle_n, self.nozzle, wait_time=1)
        initialization = '<PUMP1, ' + speed + ', ' + \
                         str(self.motor_values[0]) +'>'
        remove_drip = '<PUMP1, ' + speed + ', ' + \
                      str(self.motor_values[1]) + '>'
        dispense = '<PUMP1, ' + speed + ', ' + \
                   str(self.motor_values[2]) + '>'
        idle = '<PUMP1, '+ speed + ', ' + \
               str(self.motor_values[3]) + '>'
        initialization = bytes(initialization, 'UTF-8')
        remove_drip = bytes(remove_drip, 'UTF-8')
        dispense = bytes(dispense, 'UTF-8')
        idle = bytes(idle, 'UTF-8')

        Nozzle_change(state, self.state)
        print('Dispensing started')
        if self.wait_time[0]:
            self.send(initialization)
            time.sleep(self.wait_time[0])
        if self.wait_time[1]:
            self.send(dispense)
            time.sleep(self.wait_time[2])
        if self.wait_time[2]:
            self.send(remove_drip)
            time.sleep(self.wait_time[1])
        if self.wait_time[3]:
            self.send(idle)
            time.sleep(self.wait_time[3])
        print('Dispensing finished')
        state = self.state


class Rinse(Motor):
    def __init__(self, wait_time=[0,0,0,0,0,0,0]):
        global state
        self.wait_time = wait_time
        Motor.__init__(self)
        self.state = 2

    def run(self):
        global state
        move_down = b'<ZFLUSH, 100, +60000>'
        move_up = b'<ZFLUSH, 100, -60000>'
        flush = b'<DCPUMP4, 80, 5000>'
        equil_flush = b'<DCPUMP5, 255, 4000>'
        suc = b'<DCPUMP2, 210, 10000>'

        Nozzle_change(state, self.state)
        print('Rinsing started')
        self.send(move_down) 
        time.sleep(self.wait_time[0])
        self.send(flush)
        time.sleep(self.wait_time[1])
        self.send(suc)
        time.sleep(self.wait_time[2])
        self.send(equil_flush)
        time.sleep(self.wait_time[3])
        self.send(suc)
        time.sleep(self.wait_time[4])
        self.send(move_up)
        time.sleep(self.wait_time[5]) # [220830] newly added
        print('Rinsing finished')
        state = self.state

        
class Dry(Motor):
    def __init__(self, wait_time=[0,0,0]):
        global state
        self.wait_time = wait_time
        Motor.__init__(self)
        self.state = 3

    def run(self):
        global state
        move_down = b'<ZAIRDRY, 100, +30000>'
        blast = b'<DCPUMP3, 255, 30000>'
        move_up = b'<ZAIRDRY, 100, -30000>'

        Nozzle_change(state, self.state)
        print('Drying started')
        self.send(move_down)
        time.sleep(self.wait_time[0])
        self.send(blast)
        time.sleep(self.wait_time[1])
        self.send(move_up)
        time.sleep(self.wait_time[2])
        print('Drying finished')
        state = self.state
