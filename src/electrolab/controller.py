import serial
import time

#__options__ = ['X_STEPPER', 'Y_STEPPER', 'Z_STEPPER', 'Z_CLEANER', 'Z_ARGON', 
#               'Z_DISPENSER', 'PUMP1_STEPPER', 'PUMP2_STEPPER', 'PUMP3_STEPPER',
#               'PUMP4_STEPPER']

# Global variables
port_ = 'XXX'
baudRate = 115200

class Setup:
    def __init__(self, port, baud_rate)
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
        print('\n---')
        #self.baud_rate = baud_rate
        #self.port = port

    def send(self, message):
        ser = serial.Serial(port_, baudRate)
        #ser.readline()
        #ser.readline()
        #ser.readline()
        print('Executing command')
        ser.write(message)
        #print(ser.readline())
        #print(ser.readline())
        #print(ser.readline())
        ser.close()
        

class Dispense(Motor):
    '''
    '''

    def __init__(self, wait_time=[0,0,0,0]):
        Motor.__init__()
        #self.port = port
        #self.baud_rate = baud_rate

    def run(self):
        initialization = '<PUMP1, 1000, -3900>'
        remove_drip = '<PUMP1, 1000, +150>'
        dispense = '<PUMP1, 1000, -9100>'
        idle = '<PUMP1, 1000, +39000>'

        print('\nDispensing started')
        self.send(initialization)
        time.time(wait_time[0])
        self.send(remove_drip)
        time.time(wait_time[1])
        self.send(dispense)
        time.time(wait_time[2])
        self.send(idle)
        time.time(wait_time[3])
        print('\nDispensing finished')


class Rinse(Motor):
    def __init__(self, wait_time=[0,0,0,0,0,0,0]):
        Motor.__init()

    def run(self)
        move_down = '<ZFLUSH, 100, +60000>'
        move_up = '<ZFLUSH, 100, -60000>'
        flush = '<DCPUMP1, 30, 1500>'
        first_suc = '<DCPUMP2, 210, 30000>'
        second_suc = '<DCPUMP2, 200, 1000>'

        print('\nRinsing started')
        self.send(move_down) 
        time.time(wait_time[0])
        self.send(flush)
        time.time(wait_time[1])
        self.send(first_suc)
        time.time(wait_time[2])
        self.send(move_up)
        time.time(wait_time[3])
        self.send(move_down)
        time.time(wait_time[4])
        self.send(second_suc)
        time.time(wait_time[5])
        self.send(move_up)
        time.time(wait_time[6])
        print('\Rinsing finished')

        
class Dry(Motor):
    def __init__(self, wait_time=[0,0,0]):
        Motor.__init__()

    def run(self):
        move_down = '<ZAIRDRY, 100, +30000>'
        blast = '<DCPUMP3, 255, 30000>'
        move_up = '<ZAIRDRY, 100, -30000>'

        print('Drying started')
        self.send(move_down)
        time.time(wait_time[0])
        self.send(blast)
        time.time(wait_time[1])
        self.send(move_up)
        time.time(wait_time[2])
        print('\nDrying finished')
