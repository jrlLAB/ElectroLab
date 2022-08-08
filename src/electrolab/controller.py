import serial
import time

#__options__ = ['X_STEPPER', 'Y_STEPPER', 'Z_STEPPER', 'Z_CLEANER', 'Z_ARGON', 
#               'Z_DISPENSER', 'PUMP1_STEPPER', 'PUMP2_STEPPER', 'PUMP3_STEPPER',
#               'PUMP4_STEPPER']

# Global variables
port_ = 'XXX'
baudRate = 123
#global state
state = 1

class Setup:
    def __init__(self, port, baud_rate):
        global port_
        port_ = port
        global baudRate
        baudRate = baud_rate
        print('----------')
        print('Port: ', port_)
        print('baud_rate: ', baudRate)
        print('----------')
        

class Motor:
    def __init__(self):
        pass
        #print('\n---')
        #self.baud_rate = baud_rate
        #self.port = port

    def send(self, message):
        ser = serial.Serial(port_, baudRate)
        #ser.readline()
        #ser.readline()
        #ser.readline()
        print('Executing', message)
        ser.write(message)
        #print(ser.readline())
        #print(ser.readline())
        #print(ser.readline())
        ser.close()
        

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
        flush = b'<DCPUMP1, 30, 1500>'
        first_suc = b'<DCPUMP2, 210, 30000>'
        second_suc = b'<DCPUMP2, 200, 1000>'

        print('Rinsing started')
        self.send(move_down) 
        time.sleep(self.wait_time[0])
        self.send(flush)
        time.sleep(self.wait_time[1])
        self.send(first_suc)
        time.sleep(self.wait_time[2])
        self.send(move_up)
        time.sleep(self.wait_time[3])
        self.send(move_down)
        time.sleep(self.wait_time[4])
        self.send(second_suc)
        time.sleep(self.wait_time[5])
        self.send(move_up)
        time.sleep(self.wait_time[6])
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
