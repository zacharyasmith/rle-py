import serial, time

class Setup:
    conn = None
    
    def __init__(self):
        '''Construct setup with 9600 baud > dev/ttyUSB0'''
        self.open()
        
    def open(self):
        '''Opens connection.'''
        self.conn = serial.Serial('/dev/ttyUSB0')
        if self.conn.is_open:
            print('Connected on port: ' + self.conn.name)
        else:
            print('Could not connect...')
            return
        # Reading variable
        line = ''
        while line != b'User prgm is not valid\r\n':
            line = self.conn.readline()
            print(line)
        print('Writing "?"...')
        self.conn.write(b'?\n')
        line = ''
        while line != 'User prgm is not valid\r\n':
            line = self.conn.readline()
            print(line)
        
    def close(self):
        '''Close connection.'''
        conn.close()
       
setup = Setup();