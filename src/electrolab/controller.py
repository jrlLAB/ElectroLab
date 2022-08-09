import serial
import time
import numpy as np

#__options__ = ['X_STEPPER', 'Y_STEPPER', 'Z_STEPPER', 'Z_CLEANER', 'Z_ARGON', 
#               'Z_DISPENSER', 'PUMP1_STEPPER', 'PUMP2_STEPPER', 'PUMP3_STEPPER',
#               'PUMP4_STEPPER']

# Global variables
port_ = 'XXX'
baudRate = 123
state = 1 # Nozzle state (1: dispensing, 2: rinsing, 3: drying)
position = 0 # Head position, 0: home, 1: cell 1, 2: cell2, etc
move_speed = 1000 # Movement speed
dx0 = 4400 # dx for the home position
dx = 2000
dy = 2800

class Setup:
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
        #ser.readline()
        print('Executing', message)
        ser.write(message)
        ser.close()
        

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
    def __init__(self, cellA, cellB):
        global dx
        global dy
        global dx0
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
            #offset = dx0
            route[0] = route[0] + dx0 - dx
        elif xB == '0':
            #offset = -dx0
            route[0] = route[0] - dx0 + dx

        messageX = '<X, ' + str(move_speed) + ', ' + str(route[0]) + '>'
        messageY = '<Y, ' + str(move_speed) + ', ' + str(route[1]) + '>'
        self.message = bytes(messageX + messageY, 'UTF-8')

    def run(self):
        self.send(self.message)

       
        




class Dispense(Motor):
    '''
    '''

    def __init__(self, wait_time=[0,0,0,0]):
        self.wait_time = wait_time
        Motor.__init__(self)
        #self.port = port
        #self.baud_rate = baud_rate

    def run(self):
        global state
        print('\nInitial state', state)
        initialization = b'<PUMP1, 1000, -3900>'
        remove_drip = b'<PUMP1, 1000, +150>'
        dispense = b'<PUMP1, 1000, -9100>'
        idle = b'<PUMP1, 1000, +39000>'

        print('Dispensing started')
        self.send(initialization)
        time.sleep(self.wait_time[0])
        self.send(remove_drip)
        time.sleep(self.wait_time[1])
        self.send(dispense)
        time.sleep(self.wait_time[2])
        self.send(idle)
        time.sleep(self.wait_time[3])
        print('Dispensing finished')
        #global state
        state = 1
        print('Final state', state)


class Rinse(Motor):
    def __init__(self, wait_time=[0,0,0,0,0,0,0]):
        self.wait_time = wait_time
        Motor.__init__(self)

    def run(self):
        global state
        print('\nInitial state', state)
        move_down = b'<ZFLUSH, 100, +60000>'
        move_up = b'<ZFLUSH, 100, -60000>'
        flush = b'<DCPUMP4, 80, 5000>'
        equil_flush = b'<DCPUMP5, 255, 4000>'
        suc = b'<DCPUMP2, 210, 10000>'

        print('Rinsing started')
        self.send(move_down) 
        time.sleep(self.wait_time[0])
        self.send(flush)
        time.sleep(self.wait_time[1])
        self.send(equil_flush)
        time.sleep(self.wait_time[2])
        self.send(suc)
        time.sleep(self.wait_time[3])
        self.send(move_up)
        time.sleep(self.wait_time[4])
        print('Rinsing finished')
        #global state
        state = 2
        print('Final state', state)

        
class Dry(Motor):
    def __init__(self, wait_time=[0,0,0]):
        self.wait_time = wait_time
        Motor.__init__(self)

    def run(self):
        global state
        print('\nInitial state', state)
        move_down = b'<ZAIRDRY, 100, +30000>'
        blast = b'<DCPUMP3, 255, 30000>'
        move_up = b'<ZAIRDRY, 100, -30000>'

        print('Drying started')
        self.send(move_down)
        time.sleep(self.wait_time[0])
        self.send(blast)
        time.sleep(self.wait_time[1])
        self.send(move_up)
        time.sleep(self.wait_time[2])
        print('Drying finished')
        #global state
        state = 3
        print('Final state', state)
