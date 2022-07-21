import serial

__options__ = ['X_STEPPER', 'Y_STEPPER', 'Z_STEPPER', 'Z_CLEANER', 'Z_ARGON', 
               'Z_DISPENSER', 'PUMP1_STEPPER', 'PUMP2_STEPPER', 'PUMP3_STEPPER',
               'PUMP4_STEPPER']


class Motor:
    def __init__(self, port, baud_rate=115200):
        print('\n---')
        self.baud_rate = baud_rate
        self.port = port


    def send(self, message):
        ser = serial.Serial(self.port, self.baud_rate)
        ser.readline()
        ser.readline()
        ser.readline()
        print('Executing command')
        ser.write(message)
        print(ser.readline())
        print(ser.readline())
        print(ser.readline())
        ser.close()
        
