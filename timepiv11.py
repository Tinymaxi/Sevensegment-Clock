from datetime import datetime
import time
from time import sleep
import board
import neopixel
import RPi.GPIO as GPIO
##from multiprocessing import Process
from gpiozero import Button
from random import randint

button = Button(20)

"""Sets Neopixels up on the Raspberrypi and enables the use of 32 Neopixels."""
pixels = neopixel.NeoPixel(board.D10, 32, brightness=0.9, auto_write=True)



""" sets the value to the Neopixels to set a collor
r = 100, g = 0, b = 100 makes the color pink."""
r = 100
g = 0
b = 100


def change_colors():
    """changes the colors randomly every time the button is pressd"""
    global t,u,v,w,x,y,z
    t = randint(0,27)
    u = randint(0,27)
    v = randint(0,27)
    w = randint(0,27)
    x = randint(0,27)
    y = randint(0,27)
    z = randint(0,27)
    return t,u,v,w,x,y,z,

t,x,y,z,u,v,w=(change_colors())

button.when_pressed = change_colors


##def display_color(seconds):
##    """changes the color of all pixels when it reaches a surten number"""
##    if seconds < 10:
##        r = 120
##        g = 0
##        b = 0 
##    elif seconds > 10:
##        r = 0
##        g = 120
##        b = 0
##    elif seconds == 20:
##        r = 0
##        g = 0
##        b = 120
##        global r
##        global g
##        global b
##        return r,g,b



def digit_seconds():
    """Generates a two digit number showing the current seconds."""
    while True:
        now = datetime.now()
        currentSecond = now.second
        text = str('%02d' %(currentSecond))
        twodigit = text[0:2]
        return(int(twodigit))



def digit_minutes(f):
    """Generates a one digit number which
    can be the 1-9 minutes, or the 1-6 ten minutes part"""
    while True:
        now = datetime.now()
        currentMinute = now.minute
        text = str('%02d' %(currentMinute))
        firstdigit = text[f]
        return(int(firstdigit))
        

def digit_hours(e):
    """Generates a one digit number which
    can be the 1-9 hours, or the 1-2 ten hour part"""
    while True:
        now = datetime.now()
        currentHour = now.hour
        text = str('%02d' %(currentHour))
        firstdigit = text[e]
        return(int(firstdigit))
        
#pixel numbers and actual number form functions
def number(r,g,b,h,i,j,k,l,m,n,number):
    """ Takes the pixelnumbers and the actual number from the above
    functions. And lights up the number on the Neopixel 7-Segment."""
    if number == 0:
        pixels[h] = (r, g, b)
        pixels[i] = (r, g, b)
        pixels[j] = (r, g, b)
        pixels[k] = (r, g, b)
        pixels[l] = (r, g, b)
        pixels[m] = (r, g, b)
        pixels[n] = (0, 0, 0)
        
    elif number == 1:
        pixels[h] = (0, 0, 0)
        pixels[i] = (r, g, b)
        pixels[j] = (r, g, b)
        pixels[k] = (0, 0, 0)
        pixels[l] = (0, 0, 0)
        pixels[m] = (0, 0, 0)
        pixels[n] = (0, 0, 0)
        
    elif number == 2:
        pixels[h] = (r, g, b)
        pixels[i] = (r, g, b)
        pixels[j] = (0, 0, 0)
        pixels[k] = (r, g, b)
        pixels[l] = (r, g, b)
        pixels[m] = (0, 0, 0)
        pixels[n] = (r, g, b)

        
    elif number == 3:
        pixels[h] = (r, g, b)
        pixels[i] = (r, g, b)
        pixels[j] = (r, g, b)
        pixels[k] = (r, g, b)
        pixels[l] = (0, 0, 0)
        pixels[m] = (0, 0, 0)
        pixels[n] = (r, g, b)
        
    elif number == 4:
        pixels[h] = (0, 0, 0)
        pixels[i] = (r, g, b)
        pixels[j] = (r, g, b)
        pixels[k] = (0, 0, 0)
        pixels[l] = (0, 0, 0)
        pixels[m] = (r, g, b)
        pixels[n] = (r, g, b)

    if number == 5:
        pixels[h] = (r, g, b)
        pixels[i] = (0, 0, 0)
        pixels[j] = (r, g, b)
        pixels[k] = (r, g, b)
        pixels[l] = (0, 0, 0)
        pixels[m] = (r, g, b)
        pixels[n] = (r, g, b)       
    
    elif number == 6:
        pixels[h] = (r, g, b)
        pixels[i] = (0, 0, 0)
        pixels[j] = (r, g, b)
        pixels[k] = (r, g, b)
        pixels[l] = (r, g, b)
        pixels[m] = (r, g, b)
        pixels[n] = (r, g, b)   
        
    elif number == 7:
        pixels[h] = (r, g, b)
        pixels[i] = (r, g, b)
        pixels[j] = (r, g, b)
        pixels[k] = (0, 0, 0)
        pixels[l] = (0, 0, 0)
        pixels[m] = (0, 0, 0)
        pixels[n] = (0, 0, 0)
        
    elif number == 8:
        pixels[h] = (r, g, b)
        pixels[i] = (r, g, b)
        pixels[j] = (r, g, b)
        pixels[k] = (r, g, b)
        pixels[l] = (r, g, b)
        pixels[m] = (r, g, b)
        pixels[n] = (r, g, b)

    elif number == 9:
        pixels[h] = (r, g, b)
        pixels[i] = (r, g, b)
        pixels[j] = (r, g, b)
        pixels[k] = (r, g, b)
        pixels[l] = (0, 0, 0)
        pixels[m] = (r, g, b)
        pixels[n] = (r, g, b)

def dots(r,g,b,x):
    """ Creates a dot that moves along from side to side of the 7-Segments."""
    if x == 0 :
        pixels[7] = (r, g, b)
        pixels[15] = (0, 0, 0)
        pixels[23] = (0, 0, 0)
        pixels[31] = (0, 0, 0)        
    elif x == 1 :
        pixels[7] = (0, 0, 0)
        pixels[15] = (r, g, b)
        pixels[23] = (0, 0, 0)
        pixels[31] = (0, 0, 0)        
    elif x == 2 :
        pixels[7] = (0, 0, 0)
        pixels[15] = (0, 0, 0)
        pixels[23] = (r, g, b)
        pixels[31] = (0, 0, 0)        
    elif x == 3 :
        pixels[7] = (0, 0, 0)
        pixels[15] = (0, 0, 0)
        pixels[23] = (0, 0, 0)
        pixels[31] = (r, g, b)
    elif x == 7 :
        pixels[7] = (0, 0, 0)
        pixels[15] = (0, 0, 0)
        pixels[23] = (0, 0, 0)
        pixels[31] = (r, g, b)
    elif x == 8 :
        pixels[7] = (0, 0, 0)
        pixels[15] = (0, 0, 0)
        pixels[23] = (r, g, b)
        pixels[31] = (0, 0, 0) 
    elif x == 9 :
        pixels[7] = (0, 0, 0)
        pixels[15] = (r, g, b)
        pixels[23] = (0, 0, 0)
        pixels[31] = (0, 0, 0)
    elif x == 10 :
        pixels[7] = (r, g, b)
        pixels[15] = (0, 0, 0)
        pixels[23] = (0, 0, 0)
        pixels[31] = (0, 0, 0)
    elif x == 11 :
        pixels[7] = (0, 0, 0)
        pixels[15] = (r, g, b)
        pixels[23] = (0, 0, 0)
        pixels[31] = (0, 0, 0)
    elif x == 12 :
        pixels[7] = (0, 0, 0)
        pixels[15] = (0, 0, 0)
        pixels[23] = (r, g, b)
        pixels[31] = (0, 0, 0)        
    elif x == 13 :
        pixels[7] = (0, 0, 0)
        pixels[15] = (0, 0, 0)
        pixels[23] = (0, 0, 0)
        pixels[31] = (r, g, b)
    elif x == 17 :
        pixels[7] = (0, 0, 0)
        pixels[15] = (0, 0, 0)
        pixels[23] = (0, 0, 0)
        pixels[31] = (r, g, b)
    elif x == 18 :
        pixels[7] = (0, 0, 0)
        pixels[15] = (0, 0, 0)
        pixels[23] = (r, g, b)
        pixels[31] = (0, 0, 0) 
    elif x == 19 :
        pixels[7] = (0, 0, 0)
        pixels[15] = (r, g, b)
        pixels[23] = (0, 0, 0)
        pixels[31] = (0, 0, 0)
    elif x == 20 :
        pixels[7] = (r, g, b)
        pixels[15] = (0, 0, 0)
        pixels[23] = (0, 0, 0)
        pixels[31] = (0, 0, 0)        
    elif x == 21 :
        pixels[7] = (0, 0, 0)
        pixels[15] = (r, g, b)
        pixels[23] = (0, 0, 0)
        pixels[31] = (0, 0, 0)        
    elif x == 22 :
        pixels[7] = (0, 0, 0)
        pixels[15] = (0, 0, 0)
        pixels[23] = (r, g, b)
        pixels[31] = (0, 0, 0)        
    elif x == 23 :
        pixels[7] = (0, 0, 0)
        pixels[15] = (0, 0, 0)
        pixels[23] = (0, 0, 0)
        pixels[31] = (r, g, b)
    elif x == 27 :
        pixels[7] = (0, 0, 0)
        pixels[15] = (0, 0, 0)
        pixels[23] = (0, 0, 0)
        pixels[31] = (r, g, b)
    elif x == 28 :
        pixels[7] = (0, 0, 0)
        pixels[15] = (0, 0, 0)
        pixels[23] = (r, g, b)
        pixels[31] = (0, 0, 0) 
    elif x == 29 :
        pixels[7] = (0, 0, 0)
        pixels[15] = (r, g, b)
        pixels[23] = (0, 0, 0)
        pixels[31] = (0, 0, 0)
    elif x == 30 :
        pixels[7] = (r, g, b)
        pixels[15] = (0, 0, 0)
        pixels[23] = (0, 0, 0)
        pixels[31] = (0, 0, 0)        
    elif x == 31 :
        pixels[7] = (0, 0, 0)
        pixels[15] = (r, g, b)
        pixels[23] = (0, 0, 0)
        pixels[31] = (0, 0, 0)        
    elif x == 32 :
        pixels[7] = (0, 0, 0)
        pixels[15] = (0, 0, 0)
        pixels[23] = (r, g, b)
        pixels[31] = (0, 0, 0)        
    elif x == 33 :
        pixels[7] = (0, 0, 0)
        pixels[15] = (0, 0, 0)
        pixels[23] = (0, 0, 0)
        pixels[31] = (r, g, b)
    elif x == 37 :
        pixels[7] = (0, 0, 0)
        pixels[15] = (0, 0, 0)
        pixels[23] = (0, 0, 0)
        pixels[31] = (r, g, b)
    elif x == 38 :
        pixels[7] = (0, 0, 0)
        pixels[15] = (0, 0, 0)
        pixels[23] = (r, g, b)
        pixels[31] = (0, 0, 0) 
    elif x == 39 :
        pixels[7] = (0, 0, 0)
        pixels[15] = (r, g, b)
        pixels[23] = (0, 0, 0)
        pixels[31] = (0, 0, 0)
    elif x == 40 :
        pixels[7] = (r, g, b)
        pixels[15] = (0, 0, 0)
        pixels[23] = (0, 0, 0)
        pixels[31] = (0, 0, 0)
    elif x == 41 :
        pixels[7] = (0, 0, 0)
        pixels[15] = (r, g, b)
        pixels[23] = (0, 0, 0)
        pixels[31] = (0, 0, 0)
    elif x == 42 :
        pixels[7] = (0, 0, 0)
        pixels[15] = (0, 0, 0)
        pixels[23] = (r, g, b)
        pixels[31] = (0, 0, 0)        
    elif x == 43 :
        pixels[7] = (0, 0, 0)
        pixels[15] = (0, 0, 0)
        pixels[23] = (0, 0, 0)
        pixels[31] = (r, g, b)
    elif x == 47 :
        pixels[7] = (0, 0, 0)
        pixels[15] = (0, 0, 0)
        pixels[23] = (0, 0, 0)
        pixels[31] = (r, g, b)
    elif x == 48 :
        pixels[7] = (0, 0, 0)
        pixels[15] = (0, 0, 0)
        pixels[23] = (r, g, b)
        pixels[31] = (0, 0, 0) 
    elif x == 49 :
        pixels[7] = (0, 0, 0)
        pixels[15] = (r, g, b)
        pixels[23] = (0, 0, 0)
        pixels[31] = (0, 0, 0)
    elif x == 50 :
        pixels[7] = (r, g, b)
        pixels[15] = (0, 0, 0)
        pixels[23] = (0, 0, 0)
        pixels[31] = (0, 0, 0)        
    elif x == 51 :
        pixels[7] = (0, 0, 0)
        pixels[15] = (r, g, b)
        pixels[23] = (0, 0, 0)
        pixels[31] = (0, 0, 0)        
    elif x == 52 :
        pixels[7] = (0, 0, 0)
        pixels[15] = (0, 0, 0)
        pixels[23] = (r, g, b)
        pixels[31] = (0, 0, 0)        
    elif x == 53 :
        pixels[7] = (0, 0, 0)
        pixels[15] = (0, 0, 0)
        pixels[23] = (0, 0, 0)
        pixels[31] = (r, g, b)
    elif x == 57 :
        pixels[7] = (0, 0, 0)
        pixels[15] = (0, 0, 0)
        pixels[23] = (0, 0, 0)
        pixels[31] = (r, g, b)
    elif x == 58 :
        pixels[7] = (0, 0, 0)
        pixels[15] = (0, 0, 0)
        pixels[23] = (r, g, b)
        pixels[31] = (0, 0, 0) 
    elif x == 59 :
        pixels[7] = (0, 0, 0)
        pixels[15] = (r, g, b)
        pixels[23] = (0, 0, 0)
        pixels[31] = (0, 0, 0)
    else:
        pixels[7] = (0, 0, 0)
        pixels[15] = (0, 0, 0)
        pixels[23] = (0, 0, 0)
        pixels[31] = (0, 0, 0)


"""
Set up pins for dezimal
SDI   = 19
RCLK  = 13
SRCLK = 6
Set up pins for singular"""

SDI   = 18
RCLK  = 27
SRCLK = 22

"""Original code with out dots"""
##segCode = [0x6D6f,0x6D7f,0x6D07,0x6D7d,0x6D6d,0x6D66,0x6D4f,0x6D5b,0x6d06,0x6d3f,
##           0x666f,0x667f,0x6607,0x667d,0x666d,0x6666,0x664f,0x665b,0x6606,0x663f,
##           0x4f6f,0x4f7f,0x4f07,0x4f7d,0x4f6d,0x4f66,0x4f4f,0x4f5b,0x4f06,0x4f3f,
##           0x5b6f,0x5b7f,0x5b07,0x5b7d,0x5b6d,0x5b66,0x5b4f,0x5b5b,0x5b06,0x5b3f,
##           0x066f,0x067f,0x0607,0x067d,0x066d,0x0666,0x064f,0x065b,0x0606,0x063f,
##           0x3f6f,0x3f7f,0x3f07,0x3f7d,0x3f6d,0x3f66,0x3f4f,0x3f5b,0x3f06,0x3f3f,]

""" This list contains the rows of zero and one which are passed to the shiftregister
to display the corrosponding number from 0 to 60"""
##segCode = [0x6D6f,0x6D7f,0x6D07,0xeD7d,0x6Ded,0xeD66,0x6D4f,0x6D5b,0x6d06,0x6d3f,
##           0x666f,0x667f,0x6607,0xe67d,0x66ed,0xe666,0x664f,0x665b,0x6606,0x663f,
##           0x4f6f,0x4f7f,0x4f07,0xcf7d,0x4fed,0xcf66,0x4f4f,0x4f5b,0x4f06,0x4f3f,
##           0x5b6f,0x5b7f,0x5b07,0xdb7d,0x5bed,0xdb66,0x5b4f,0x5b5b,0x5b06,0x5b3f,
##           0x066f,0x067f,0x0607,0x867d,0x06ed,0x8666,0x064f,0x065b,0x0606,0x063f,
##           0x3f6f,0x3f7f,0x3f07,0xbf7d,0x3fed,0xbf66,0x3f4f,0x3f5b,0x3f06,0x3f3f,]




segCode = [0x6f6D,0x7f6D,0x076D,0x7deD,0xed6D,0x66eD,0x4f6D,0x5b6D,0x066D,0x3f6D, 
           0x6f66,0x7f66,0x0766,0x7de6,0xed66,0x66e6,0x4f66,0x5b66,0x0666,0x3f66, 
           0x6f4f,0x7f4f,0x074f,0x7dcf,0xed4f,0x66cf,0x4f4f,0x5b4f,0x064f,0x3f4f, 
           0x6f5b,0x7f5b,0x075b,0x7ddb,0xed5b,0x66db,0x4f5b,0x5b5b,0x065b,0x3f5b, 
           0x6f06,0x7f06,0x0706,0x7d86,0xed06,0x6686,0x4f06,0x5b06,0x0606,0x3f06,
           0x6f3f,0x7f3f,0x073f,0x7dbf,0xed3f,0x66bf,0x4f3f,0x5b3f,0x063f,0x3f3f,]




def setup():
    """sets up the pins"""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SDI, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(RCLK, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(SRCLK, GPIO.OUT, initial=GPIO.LOW)    


def hc595_shift(dat):
    """Shifts the data to 74HC595"""
    for bit in range(0, 16): 
        GPIO.output(SDI, 0x8000 & (dat << bit))
        GPIO.output(SRCLK, GPIO.HIGH)
        time.sleep(0.001)
        GPIO.output(SRCLK, GPIO.LOW)
    GPIO.output(RCLK, GPIO.HIGH)
    time.sleep(0.001)
    GPIO.output(RCLK, GPIO.LOW)


def main():
    while True:
        """calls the funktions and passes in the parameters."""
#        print(digit_hours(0),digit_hours(1),digit_minutes(0),digit_minutes(1),digit_seconds())

#        display_color(100,20,30,digit_seconds())
        
        Seconds = digit_seconds()
        dat = segCode[-Seconds-1]
        hc595_shift(dat)
           
        number(x,y,z,0,1,2,3,4,5,6,digit_hours(0))        
        number(x,y,z,8,9,10,11,12,13,14,digit_hours(1))
        number(u,v,w,16,17,18,19,20,21,22,digit_minutes(0))        
        number(u,v,w,24,25,26,27,28,29,30,digit_minutes(1))

        dots(t,y,w,digit_seconds())        
#        time.sleep(0.33)
def destroy():
    """Stuff I don't realy understand"""
    GPIO.cleanup()

if __name__ == '__main__':
        setup()
        try:
            
            main()
                
        except:
            pass

