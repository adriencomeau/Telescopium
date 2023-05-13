# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import serial
import time

def my_function(cmd_bytes):
    serPort.write(cmd_bytes)
    response = serPort.read_until(bytes(0X23),None)
    print ('TX:   ',cmd_bytes,'    Rx:    ',response)
    return response

serialPortStr = '/dev/CelestronCGEPro'
#serialPortStr = '/dev/ttyUSB0'
serPort = serial.Serial(serialPortStr)  # open serial port
if not(serPort.isOpen()):
    ExcMsg='crap'
    raise Exception(ExcMsg)


serPort.baudrate = 9600
serPort.bytesize = serial.EIGHTBITS #number of bits per bytes
serPort.parity = serial.PARITY_NONE #set parity check: no parity
serPort.stopbits = serial.STOPBITS_ONE #number of stop bits
serPort.timeout = 1         #block read
serPort.xonxoff = False     #disable software flow control
serPort.rts = False     #disable hardware (RTS/CTS) flow control
serPort.dsrdtr = False       #disable hardware (DSR/DTR) flow control
serPort.writeTimeout = 0     #timeout for write

#print('OPEN serial port.')
#serPort.open()

print('FLUSH serial port.')
serPort.flushInput()
serPort.flushOutput()

print('Start...')
print('V ... Get Version (see pdf)')
my_function([0X56])

print('T 0 ... Set Tracking Mode OFF (see pdf)')
my_function([0X54,0X00])

print('P 1 17 5 0 0 0 1 ... ??')
my_function([0X50,0X01,0X11,0X05,0X00,0X00,0X00,0X01]) 

print('P 1 16 5 0 0 0 1 ... ??')
my_function([0X50,0X01,0X10,0X05,0X00,0X00,0X00,0X01])



print('P 1 dev 254 0 0 0 2... Get Device (AZM/RA Motor) Version (see pdf)')
my_function([0X50,0X01,0X10,0XFE,0X00,0X00,0X00,0X02])



print('P 1 16 252 0 0 0 2   ... AZM=16 MC_GET_APPROACH=252/0xFC (in paq family pdf)')
my_function([0X50,0X01,0X10,0XFC,0X00,0X00,0X00,0X02]) 
print('P 1 17 252 0 0 0 2   ... ALT=17 MC_GET_APPROACH=252/0xFC (in paq family pdf)')
my_function([0X50,0X01,0X11,0XFC,0X00,0X00,0X00,0X02]) 



print('P 4 16 4 4 0 0 0     ... AZM=16 MC_SET_POSITION=4/0x04 (in paq family pdf) (not in pdf)')
my_function([0X50,0X04,0X10,0X04,0X40,0X00,0X00,0X00])
print('P 4 17 4 4 0 0       ... ALT=17 MC_SET_POSITION=4/0x04 (in paq family pdf) (not in pdf)')
my_function([0X50,0X04,0X11,0X04,0X40,0X00,0X00,0X00])



print('P 4 16 58 192 0 0 0  ... AZM=16  MC_SET_CORDWRAP_POS=58/0x3A (in paq family pdf) (not in pdf)')
my_function([0X50,0X04,0X10,0X3A,0XC0,0X00,0X00,0X00])
print('P 1 16 56 0 0 0 0    ... AZM=16  MC_ENABLE_CORDWRAP=56/0x38 (in paq family pdf) (not in pdf)')
my_function([0X50,0X01,0X10,0X38,0X00,0X00,0X00,0X00])
print('P 4 17 58 192 0 0 0  ... ALT=17  MC_SET_CORDWRAP_POS=58/0x3A (in paq family pdf) (not in pdf)')
my_function([0X50,0X04,0X11,0X3A,0XC0,0X00,0X00,0X00])       
print('P 1 17 56 0 0 0 0    ... ALT=17  MC_ENABLE_CORDWRAP=56/0x38 (in paq family pdf) (not in pdf)')
my_function([0X50,0X01,0X11,0X38,0X00,0X00,0X00,0X00])

#PRESS Enter to begin alignmenty
#press enter to move to switch position


print('P 4 16 6 0 0 0 0     ... AZM=16  MC_SET_POS_GUIDERATE=6/0x06 (in paq family pdf) (not in pdf)')
my_function([0X50,0X04,0X10,0X06,0X00,0X00,0X00,0X00])
print('P 4 17 6 0 0 0 0     ... ALT=17  MC_SET_POS_GUIDERATE=6/0x06 (in paq family pdf) (not in pdf)')
my_function([0X50,0X04,0X11,0X06,0X00,0X00,0X00,0X00])


print('P 1 16 11 0 0 0 0    ... ALT=16  MC_LEVEL_START=11/0x0B (in paq family pdf) (not in pdf)')
my_function([0X50,0X01,0X10,0X0B,0X00,0X00,0X00,0X00])
print('P 1 17 11 0 0 0 0    ... ALT=17  MC_LEVEL_START=11/0x0B (in paq family pdf) (not in pdf)')
my_function([0X50,0X01,0X11,0X0B,0X00,0X00,0X00,0X00])



print('P 1 16 18 0 0 0 0    ... AZM=16  MC_LEVEL_DONE=18/0x12 (in paq family pdf) (in paq family pdf)')
response =     my_function([0X50,0X01,0X10,0X12,0X00,0X00,0X00,0X01])        
while (response[0] == 0x00) :
    response = my_function([0X50,0X01,0X10,0X12,0X00,0X00,0X00,0X01])
    time.sleep(0.5)
    
print('P 1 17 18 0 0 0 0    ... ALT=17  MC_LEVEL_DONE=18/0x12 (in paq family pdf) (in paq family pdf)')
response =     my_function([0X50,0X01,0X11,0X12,0X00,0X00,0X00,0X01])
while (response[0] == 0x00):
    response = my_function([0X50,0X01,0X11,0X12,0X00,0X00,0X00,0X01])
    time.sleep(0.5)

# time in     

print('P 4 16 4 64 0 0 0    ... AZM=16  MC_SET_POSITION=4/0x04 (in paq family pdf) (not in pdf)')
my_function([0X50,0X04,0X10,0X04,0X40,0X00,0X00,0X00])
print('P 4 17 4 64 0 0 0    ... AZM=17  MC_SET_POSITION=4/0x04 (in paq family pdf) (not in pdf)')
my_function([0X50,0X04,0X11,0X04,0X40,0X00,0X00,0X00])



print('P 4 16 58 192 0 0 0  ... AZM=16  MC_SET_CORDWRAP_POS=58/0x3A (in paq family pdf) (not in pdf)')
my_function([0X50,0X04,0X10,0X3A,0XC0,0X00,0X00,0X00]) 
print('P 1 16 56 0 0 0 0    ... AZM=16  MC_ENABLE_CORDWRAP=56/0x38 (in paq family pdf) (not in pdf)')
my_function([0X50,0X01,0X10,0X38,0X00,0X00,0X00,0X00])
print('P 4 17 58 192 0 0 0  ... ALT=17  MC_SET_CORDWRAP_POS=58/0x3A (in paq family pdf) (not in pdf)')
my_function([0X50,0X04,0X11,0X3A,0XC0,0X00,0X00,0X00])
print('P 1 17 6 0 0 0 0     ... ALT=17  MC_ENABLE_CORDWRAP=56/0x38 (in paq family pdf) (not in pdf)')
my_function([0X50,0X01,0X11,0X38,0X00,0X00,0X00,0X00])



print('P 4 16 6 0 0 0 0     ... AZM=16  MC_SET_POS_GUIDERATE=6/0x06 (in paq family pdf) (not in pdf)')
my_function([0X50,0X04,0X10,0X06,0X00,0X00,0X00,0X00])
print('P 4 17 6 0 0 0 0     ... ALT=17  MC_SET_POS_GUIDERATE=6/0x06 (in paq family pdf) (not in pdf)')
my_function([0X50,0X04,0X11,0X06,0X00,0X00,0X00,0X00])



print('P 3 16 6 255 255 0 0 ... AZM=16  MC_SET_POS_GUIDERATE=6/0x06 sidereal (in paq family pdf) (see pdf)')
my_function([0X50,0X03,0X10,0X06,0XFF,0XFF,0X00,0X00]) 


print('CLOSE serial port.')
serPort.close()
print('Done:')

    