#!/usr/bin/python
from datetime import datetime, date, timedelta
import math
import time
from time import sleep
import board
import neopixel
import RPi.GPIO as  GPIO
from gpiozero import Button
from random import random
import colorsys
import sys
from subprocess import check_call, check_output, DEVNULL
import traceback
from signal import pause

button = Button(20)


"""Sets Neopixels up on the Raspberrypi and enables the use of 32 Neopixels."""
pixels = neopixel.NeoPixel(board.D18, 32, brightness=0.9, auto_write = True)



"""Suhtdown"""
def shutdown():
    check_call(['sudo', 'poweroff'])


"""The colours. A short press of the button goes to the next colour
pattern: first the 15 fixed ones in COLOR_SETTINGS below, after that every
press makes a new random one. When the button has not been pressed for a
minute, the next press starts with number 1 again. After switching on, the
clock shows a random one.

A pattern can give every single segment its own colour, and it can move.
Every colour is (red, green, blue), each from 0 to 27."""

"""Where the segments sit inside a digit. The seven pixels of a digit are
the segments a to g (a top, b top right, c bottom right, d bottom,
e bottom left, f top left, g middle), number 7 is the dot."""
SEGMENT_X = (0.5, 1.0, 1.0, 0.5, 0.0, 0.0, 0.5, 1.3)       # 0 is left, 1 is right
SEGMENT_Y = (0.0, 0.25, 0.75, 1.0, 0.75, 0.25, 0.5, 1.0)    # 0 is top, 1 is bottom
DIGIT_SEGMENTS = ('abcdef', 'bc', 'abdeg', 'abcdg', 'bcfg',
                  'acdfg', 'acdefg', 'abc', 'abcdefg', 'abcdfg')
MOVING_DOT = {0: 0, 1: 1, 2: 2, 3: 3, 7: 3, 8: 2, 9: 1}    # which dot is on in which second


def mix(color1, color2, p):
    """Mixes two colours. p = 0 gives color1, p = 1 gives color2."""
    return tuple(int(round(a + (b - a) * p)) for a, b in zip(color1, color2))


def blend(stops, p):
    """Runs through a list of colours. p = 0 gives the first, p = 1 the last."""
    p = max(0.0, min(1.0, p)) * (len(stops) - 1)
    i = min(int(p), len(stops) - 2)
    return mix(stops[i], stops[i + 1], p - i)


def wheel(hue, brightness=1.0):
    """A strong colour from the colour wheel. hue runs from 0.0 to 1.0:
    0 red, 0.17 yellow, 0.33 green, 0.5 cyan, 0.67 blue, 0.83 magenta."""
    r, g, b = colorsys.hsv_to_rgb(hue % 1.0, 1, 1)
    return (int(round(r * 27 * brightness)), int(round(g * 27 * brightness)),
            int(round(b * 27 * brightness)))


def across(digit, segment):
    """Where a segment sits on the whole clock: 0.0 far left, 1.0 far right."""
    return (digit + SEGMENT_X[segment] * 0.6) / 3.6


def noise(n):
    """A fixed pseudo random number between 0 and 1 for the number n."""
    return (math.sin(n * 12.9898) * 43758.5453) % 1.0


def flicker(digit, segment, t):
    """A value between 0 and 1 that wanders smoothly over time, different
    for every segment. t counts the steps."""
    seed = (digit * 8 + segment) * 57
    step = int(t)
    a = noise(seed + step)
    b = noise(seed + step + 1)
    return a + (b - a) * (t - step)


"""The pattern makers. Each one returns a pattern. A pattern is asked for
the colour of one segment: which digit (0 to 3), which segment (0 to 7)
and the time t in seconds, which the moving patterns use."""


def split(hours, minutes):
    """Uses one pattern for the hours and another one for the minutes, so
    the two can always be told apart."""
    def pattern(digit, segment, t):
        if digit < 2:
            return hours(digit, segment, t)
        return minutes(digit, segment, t)
    return pattern


def parts(hours, minutes, dot):
    """Hours in one colour, minutes in another."""
    def pattern(digit, segment, t):
        if segment == 7:
            return dot
        return hours if digit < 2 else minutes
    return pattern


def per_digit(first, second, third, fourth, dot):
    """Each of the four digits in its own colour."""
    def pattern(digit, segment, t):
        if segment == 7:
            return dot
        return (first, second, third, fourth)[digit]
    return pattern


def top_to_bottom(*stops):
    """The colours run from the top of the digits to the bottom."""
    def pattern(digit, segment, t):
        return blend(stops, SEGMENT_Y[segment])
    return pattern


def left_to_right(*stops):
    """The colours run from the left of the clock to the right."""
    def pattern(digit, segment, t):
        return blend(stops, across(digit, segment))
    return pattern


def two_tone(lying, standing, dot):
    """The lying segments in one colour, the standing ones in another."""
    def pattern(digit, segment, t):
        if segment == 7:
            return dot
        return lying if segment in (0, 3, 6) else standing
    return pattern


def rainbow(seconds_per_round):
    """A rainbow across the clock. It moves once around in the given number
    of seconds, 0 lets it stand still."""
    def pattern(digit, segment, t):
        shift = t / seconds_per_round if seconds_per_round else 0
        return wheel(across(digit, segment) * 0.85 - shift)
    return pattern


def aurora(hue_from, hue_to):
    """Northern lights: the colours drift slowly between two places on the
    colour wheel, for example 0.33 (green) and 0.75 (violet)."""
    def pattern(digit, segment, t):
        x = across(digit, segment)
        y = SEGMENT_Y[segment]
        wave = 0.5 + 0.5 * math.sin(t * 0.45 + x * 5.0 + y * 2.0)
        glow = 0.6 + 0.4 * math.sin(t * 0.7 + x * 8.0 - y * 3.0)
        return wheel(hue_from + (hue_to - hue_from) * wave, glow)
    return pattern


def fire(*flame):
    """Flames that flicker. The colours run from the top of the flame to
    the bottom."""
    def pattern(digit, segment, t):
        return mix((0, 0, 0), blend(flame, SEGMENT_Y[segment]), 0.4 + 0.6 * flicker(digit, segment, t * 7))
    return pattern


def waves(*stops):
    """Waves: the colours roll across the clock from left to right."""
    def pattern(digit, segment, t):
        x = across(digit, segment)
        y = SEGMENT_Y[segment]
        return blend(stops, 0.5 + 0.5 * math.sin(x * 6.0 - t * 1.2 + y * 1.5))
    return pattern


def scanner(dark, bright):
    """A bright spot that sweeps from side to side over a dark clock."""
    def pattern(digit, segment, t):
        spot = abs((t / 1.5) % 2.0 - 1.0)
        glow = max(0.0, 1.0 - abs(across(digit, segment) - spot) * 3.5)
        return mix(dark, bright, glow)
    return pattern


def lava(hue):
    """Lava: colours flowing slowly into each other around one place on
    the colour wheel, for example 0.03 (red and orange) or 0.92 (pink)."""
    def pattern(digit, segment, t):
        x = across(digit, segment)
        y = SEGMENT_Y[segment]
        return wheel(hue + 0.07 * math.sin(t * 0.35 + x * 4.0 + y * 2.5))
    return pattern


def stars(sky, star):
    """A night sky in which single segments twinkle."""
    def pattern(digit, segment, t):
        if noise((digit * 8 + segment) * 31 + int(t * 3)) < 0.06:
            return star
        return sky
    return pattern


def time_wheel():
    """The colour shows the minutes: the hours go once around the colour
    wheel every hour. Red on the hour, green at 20 past, blue at 20 to.
    The minutes are always a little further around the wheel."""
    def pattern(digit, segment, t):
        now = datetime.now()
        hue = (now.minute * 60 + now.second) / 3600.0
        if digit >= 2:
            hue = hue + 0.15
        return wheel(hue)
    return pattern


WHITE = (20, 20, 20)
PINK = (27, 0, 14)
CYAN = (0, 24, 24)
GOLD = (27, 18, 0)
VIOLET = (14, 0, 27)
"""In every pattern the hours look different from the minutes."""
COLOR_SETTINGS = [
    # evening sky: the hours violet to amber, the minutes lower down near the sun
    ('Horizon',       split(top_to_bottom((6, 0, 27), (27, 0, 14), (27, 14, 0)),
                            top_to_bottom((27, 0, 14), (27, 14, 0), (27, 24, 0)))),
    ('Rainbow',       rainbow(0)),
    # the hours burn red, the minutes hotter and more yellow
    ('Fire',          split(fire((27, 0, 0), (27, 5, 0), (27, 14, 0)),
                            fire((27, 10, 0), (27, 20, 0), (27, 27, 6)))),
    # rolling waves: the hours deep blue, the minutes sea green
    ('Ocean',         split(waves((0, 2, 27), (0, 10, 27), (0, 20, 24)),
                            waves((0, 18, 22), (0, 24, 12), (0, 27, 4)))),
    # northern lights: the hours green to turquoise, the minutes blue to violet
    ('Aurora',        split(aurora(0.30, 0.50), aurora(0.58, 0.80))),
    # pink and cyan, swapped between hours and minutes
    ('Neon',          split(two_tone(PINK, CYAN, (27, 22, 0)), two_tone(CYAN, PINK, (27, 22, 0)))),
    ('Candy',         per_digit((27, 0, 16), (27, 10, 0), (27, 24, 0), (0, 27, 12), WHITE)),
    # white to deep blue, the minutes upside down like a reflection
    ('Ice',           split(top_to_bottom(WHITE, (0, 22, 27), (0, 2, 27)),
                            top_to_bottom((0, 2, 27), (0, 22, 27), WHITE))),
    # the hours red and orange, the minutes pink
    ('Lava',          split(lava(0.07), lava(0.86))),
    ('Rainbow flow',  rainbow(20)),
    # a sweeping spot: red over the hours, amber over the minutes
    ('Scanner',       split(scanner((6, 0, 0), (27, 2, 0)), scanner((5, 4, 0), (27, 16, 0)))),
    # twinkling stars: the hours in a blue sky, the minutes in a violet one
    ('Stars',         split(stars((0, 3, 22), WHITE), stars((9, 0, 22), WHITE))),
    # gold and violet, swapped between hours and minutes
    ('Royal',         split(two_tone(GOLD, VIOLET, WHITE), two_tone(VIOLET, GOLD, WHITE))),
    ('Swiss',         parts((27, 0, 0), WHITE, (27, 0, 0))),
    ('Time wheel',    time_wheel()),
]
COLOR_RESTART_AFTER = 60    # seconds without a press, after which the next press starts with number 1 again

colors = {'position': None, 'name': '', 'pattern': None, 'hue': None, 'last_press': None}


def random_hue(avoid):
    """Picks a random colour on the colour wheel (0.0 to 1.0) that is not
    too close to the colours in the list avoid."""
    while True:
        hue = random()
        if all(min(abs(hue - a), 1 - abs(hue - a)) >= 0.12 for a in avoid):
            return hue


def random_colors():
    """Makes a random pattern: random strong colours that differ from each
    other and from the random pattern before, in a random arrangement."""
    avoid = []
    if colors['hue'] is not None:
        avoid.append(colors['hue'])
    hue1 = random_hue(avoid)
    hue2 = random_hue([hue1])
    hue3 = random_hue([hue1, hue2])
    hue4 = random_hue([hue1, hue3])
    c1, c2, c3, c4 = wheel(hue1), wheel(hue2), wheel(hue3), wheel(hue4)
    kind = int(random() * 6)
    if kind == 0:
        name, pattern = 'hours and minutes', parts(c1, c2, c3)
    elif kind == 1:
        name, pattern = 'four digits', per_digit(c1, c2, c3, c4, WHITE)
    elif kind == 2:
        name, pattern = 'top to bottom', split(top_to_bottom(c1, c2), top_to_bottom(c2, c1))
    elif kind == 3:
        name, pattern = 'left to right', left_to_right(c1, c2, c3)
    elif kind == 4:
        name, pattern = 'two tone', split(two_tone(c1, c2, c3), two_tone(c2, c1, c3))
    else:
        name, pattern = 'top to bottom, three colours', split(top_to_bottom(c1, c2, c3), top_to_bottom(c3, c2, c1))
    colors['hue'] = hue1
    colors['name'] = 'Random (' + name + ')'
    colors['pattern'] = pattern


def change_colors():
    """goes to the next colour pattern every time the button is pressed"""
    now = time.monotonic()
    if colors['position'] is None:
        """the clock has just been switched on: a random one"""
        colors['position'] = len(COLOR_SETTINGS)
    else:
        if colors['last_press'] is None or now - colors['last_press'] >= COLOR_RESTART_AFTER:
            colors['position'] = 0
        else:
            colors['position'] = min(colors['position'] + 1, len(COLOR_SETTINGS))
        colors['last_press'] = now
    if colors['position'] < len(COLOR_SETTINGS):
        colors['name'], colors['pattern'] = COLOR_SETTINGS[colors['position']]
    else:
        random_colors()
    print('Colours:', colors['name'], flush=True)


change_colors()


def draw_pattern(pattern):
    """Draws the time and the moving dot with a colour pattern."""
    t = time.monotonic()
    values = (digit_hours(0), digit_hours(1), digit_minutes(0), digit_minutes(1))
    dot = MOVING_DOT.get(digit_seconds() % 10)
    """All pixels are sent to the clock in one go, that makes the moving
    patterns run smoothly."""
    pixels.auto_write = False
    try:
        for digit in range(4):
            lit = DIGIT_SEGMENTS[values[digit]]
            if digit == 0 and values[0] == 0:
                lit = ''
            for segment in range(7):
                if 'abcdefg'[segment] in lit:
                    pixels[digit * 8 + segment] = pattern(digit, segment, t)
                else:
                    pixels[digit * 8 + segment] = (0, 0, 0)
            if digit == dot:
                pixels[digit * 8 + 7] = pattern(digit, 7, t)
            else:
                pixels[digit * 8 + 7] = (0, 0, 0)
        pixels.show()
    finally:
        pixels.auto_write = True


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


SDI   = 23
RCLK  = 27
SRCLK = 22

""" This list contains the rows of zero and one which are passed to the shiftregister
to display the corrosponding number from 0 to 60"""

segCode = [0x6f6D,0x7f6D,0x076D,0x7deD,0xed6D,0x66eD,0x4f6D,0x5b6D,0x066D,0x3f6D, 
           0x6f66,0x7f66,0x0766,0x7de6,0xed66,0x66e6,0x4f66,0x5b66,0x0666,0x3f66, 
           0x6f4f,0x7f4f,0x074f,0x7dcf,0xed4f,0x66cf,0x4f4f,0x5b4f,0x064f,0x3f4f, 
           0x6f5b,0x7f5b,0x075b,0x7ddb,0xed5b,0x66db,0x4f5b,0x5b5b,0x065b,0x3f5b, 
           0x6f06,0x7f06,0x0706,0x7d86,0xed06,0x6686,0x4f06,0x5b06,0x0606,0x3f06,
           0x6f3f,0x7f3f,0x073f,0x7dbf,0xed3f,0x66bf,0x4f3f,0x5b3f,0x063f,0x3f3f,]




"""Night mode, sunset colour and the button.

Night (23:00 to 6:00): faint red digits, one blinking dot, seconds off.
The hour before sunset: the digits take a sunset colour that gets redder
the closer the sunset is. Sunset is calculated here on the Pi for the
place below, so no internet is needed.

Button: short press                  = next colour pattern
        hold 2 seconds, then let go  = Wi-Fi on or off
        hold 6 seconds               = switch the Pi off"""
LATITUDE = 47.2088          # Solothurn
LONGITUDE = 7.5323          # east is positive
NIGHT_START = (23, 0)       # (hour, minute) when night mode begins
NIGHT_END = (6, 0)          # (hour, minute) when night mode ends
NIGHT_COLOR = (4, 0, 0)     # (red, green, blue), 0-255 each, higher = brighter
NIGHT_SECONDS_OFF = True    # True: seconds display is dark at night
NIGHT_DOT_PIXEL = 15        # dot that blinks at night, between hours and minutes (the dots are pixels 7, 15, 23, 31)
SUNSET_WARNING_MIN = 60     # the sunset colour starts this many minutes before sunset
SUNSET_COLOR_START = (27, 14, 0)    # amber, at the start of the warning
SUNSET_COLOR_END = (27, 2, 1)       # deep red, at sunset
WIFI_HOLD = 2               # hold the button this many seconds for Wi-Fi on/off
SHUTDOWN_HOLD = 6           # hold the button this many seconds to switch the Pi off
WIFI_CONNECT_TIMEOUT = 60   # seconds to wait for the Wi-Fi to connect
WIFI_RETRY_AFTER = 20       # if it is not connected after this many seconds, try to join again
WIFI_COLOR = (0, 6, 27)     # blue, used while switching the Wi-Fi
WIFI_OK_COLOR = (0, 27, 0)  # green, Wi-Fi is connected
ERROR_COLOR = (27, 0, 0)    # red, Wi-Fi did not connect
SHUTDOWN_COLOR = (27, 0, 0) # red, "bYE" before the Pi switches off


def sun_times_utc(day):
    """Returns sunrise and sunset of the given date as UTC datetimes."""
    n = day.toordinal() - date(2000, 1, 1).toordinal()
    noon = n - LONGITUDE / 360.0
    M = math.radians((357.5291 + 0.98560028 * noon) % 360)
    C = 1.9148 * math.sin(M) + 0.02 * math.sin(2 * M) + 0.0003 * math.sin(3 * M)
    lam = math.radians((math.degrees(M) + C + 180 + 102.9372) % 360)
    transit = noon + 0.0053 * math.sin(M) - 0.0069 * math.sin(2 * lam)
    decl = math.asin(math.sin(lam) * math.sin(math.radians(23.4397)))
    lat = math.radians(LATITUDE)
    cos_w = ((math.sin(math.radians(-0.833)) - math.sin(lat) * math.sin(decl))
             / (math.cos(lat) * math.cos(decl)))
    cos_w = max(-1.0, min(1.0, cos_w))
    w = math.degrees(math.acos(cos_w)) / 360.0
    j2000 = datetime(2000, 1, 1, 12)
    return (j2000 + timedelta(days=transit - w), j2000 + timedelta(days=transit + w))


def mode_at(local_now, utc_now):
    """Works out the mode for a moment in time. Returns the mode ('night',
    'sunset' or 'day') and how far the sunset warning has got (0.0 to 1.0)."""
    hm = (local_now.hour, local_now.minute)
    if NIGHT_START > NIGHT_END:
        night = hm >= NIGHT_START or hm < NIGHT_END
    else:
        night = NIGHT_START <= hm < NIGHT_END
    if night:
        return 'night', 0.0
    sunset = sun_times_utc(utc_now.date())[1]
    warning = sunset - timedelta(minutes=SUNSET_WARNING_MIN)
    if warning <= utc_now < sunset:
        return 'sunset', (utc_now - warning).total_seconds() / (sunset - warning).total_seconds()
    return 'day', 0.0


mode_cache = {'checked': None, 'mode': 'day', 'progress': 0.0}


def clock_mode():
    """Returns the current mode. Works it out again every 10 seconds."""
    if mode_cache['checked'] is None or time.monotonic() - mode_cache['checked'] >= 10:
        mode, progress = mode_at(datetime.now(), datetime.utcnow())
        if mode_cache['checked'] is None or mode != mode_cache['mode']:
            print('Clock mode:', mode, flush=True)
        mode_cache['checked'] = time.monotonic()
        mode_cache['mode'] = mode
        mode_cache['progress'] = progress
    return mode_cache['mode']


def sunset_color():
    """The sunset colour: amber an hour before sunset, deep red at sunset."""
    p = mode_cache['progress']
    return tuple(int(round(a + (b - a) * p)) for a, b in zip(SUNSET_COLOR_START, SUNSET_COLOR_END))


def night_dot(second):
    """At night only one dot is used. It blinks between the hours and the
    minutes: on for one second, off for one second."""
    for p in (7, 15, 23, 31):
        if p == NIGHT_DOT_PIXEL and second % 2 == 0:
            pixels[p] = NIGHT_COLOR
        else:
            pixels[p] = (0, 0, 0)


"""Letters for the Neopixel digits. The seven pixels of a digit are the
segments a to g: a top, b top right, c bottom right, d bottom,
e bottom left, f top left, g middle."""
LETTERS = {' ': '', 'o': 'cdeg', 'n': 'ceg', 'F': 'aefg', 'b': 'cdefg',
           'Y': 'bcdfg', 'E': 'adefg', 'r': 'eg'}


def show_segments(segments, color):
    """Lights the given segments on each of the four digits. segments is a
    list of four strings like 'adg'. The dots are switched off."""
    for digit in range(4):
        for s in range(7):
            if 'abcdefg'[s] in segments[digit]:
                pixels[digit * 8 + s] = color
            else:
                pixels[digit * 8 + s] = (0, 0, 0)
        pixels[digit * 8 + 7] = (0, 0, 0)


def show_text(text, color):
    """Shows four letters, for example ' on ' or 'bYE '."""
    show_segments([LETTERS[c] for c in text], color)


def show_bars(level, color):
    """Shows the Wi-Fi signal bars: level 0 is nothing, 1 the bottom line,
    2 bottom and middle, 3 all three lines."""
    show_segments(['dga'[:level]] * 4, color)


def show_seconds():
    """Shows the seconds on the red display, or nothing at night."""
    if clock_mode() == 'night' and NIGHT_SECONDS_OFF:
        hc595_shift(0x0000)
    else:
        hc595_shift(segCode[-digit_seconds()-1])


def wait(seconds):
    """Waits and keeps the seconds display running."""
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        show_seconds()


def wifi_is_on():
    """True when the Wi-Fi is switched on."""
    try:
        with open('/sys/class/net/wlan0/flags') as f:
            return int(f.read().strip(), 16) & 1 == 1
    except (IOError, ValueError):
        return False


def wifi_connected():
    """True when the Wi-Fi has got an address from the router. An address
    starting with 169.254 does not count, the Pi makes that one up itself
    while the router has not answered yet."""
    out = check_output(['/sbin/ip', '-4', '-o', 'addr', 'show', 'dev', 'wlan0']).decode()
    for word in out.split():
        if word.count('.') == 3 and '/' in word and not word.startswith('169.254.'):
            return True
    return False


def toggle_wifi():
    """Switches the Wi-Fi on or off and shows it on the digits.
    On:  blue bars climb like a Wi-Fi signal until it is connected,
         then a green 'on' (or a red 'Err' if it did not connect).
    Off: the blue bars go out from the top, then 'oFF'."""
    try:
        if wifi_is_on():
            for level in (3, 2, 1, 0):
                show_bars(level, WIFI_COLOR)
                wait(0.4)
            check_call(['/sbin/ip', 'link', 'set', 'wlan0', 'down'])
            show_text(' oFF', WIFI_COLOR)
            wait(2)
        else:
            check_call(['/sbin/ip', 'link', 'set', 'wlan0', 'up'])
            end = time.monotonic() + WIFI_CONNECT_TIMEOUT
            retry = time.monotonic() + WIFI_RETRY_AFTER
            connected = False
            level = 0
            while not connected and time.monotonic() < end:
                level = level % 3 + 1
                show_bars(level, WIFI_COLOR)
                wait(0.4)
                if level == 3:
                    connected = wifi_connected()
                    if not connected and time.monotonic() >= retry:
                        check_call(['/sbin/wpa_cli', '-i', 'wlan0', 'reassociate'], stdout=DEVNULL)
                        retry = time.monotonic() + WIFI_RETRY_AFTER
            if connected:
                show_text(' on ', WIFI_OK_COLOR)
            else:
                show_text('Err ', ERROR_COLOR)
            wait(2)
    except Exception:
        show_text('Err ', ERROR_COLOR)
        wait(2)


"""The button. The two functions below only note what happened, the main
loop then does the work."""
button_state = {'pressed_at': None, 'action': None}


def on_press():
    button_state['pressed_at'] = time.monotonic()


def on_release():
    start = button_state['pressed_at']
    button_state['pressed_at'] = None
    if start is None:
        return
    held = time.monotonic() - start
    if held >= SHUTDOWN_HOLD:
        return
    if held >= WIFI_HOLD:
        button_state['action'] = 'wifi'
    elif held >= 0.03 and button_state['action'] is None:
        button_state['action'] = 'colors'


def button_held_time():
    """How many seconds the button has been held down, 0 if it is not pressed."""
    start = button_state['pressed_at']
    if start is None:
        return 0
    return time.monotonic() - start


button.when_pressed = on_press
button.when_released = on_release


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


def loop_once():
    """One round of the clock. Returns False when the Pi is switching off."""
    held = button_held_time()
    if held >= SHUTDOWN_HOLD:
        show_text('bYE ', SHUTDOWN_COLOR)
        hc595_shift(0x0000)
        time.sleep(2)
        pixels.fill((0,0,0))
        shutdown()
        return False
    if held >= WIFI_HOLD:
        """shows what happens when the button is let go now"""
        if wifi_is_on():
            show_text(' oFF', WIFI_COLOR)
        else:
            show_text(' on ', WIFI_COLOR)
        show_seconds()
        return True

    action = button_state['action']
    button_state['action'] = None
    if action == 'colors':
        change_colors()
    elif action == 'wifi':
        toggle_wifi()

    mode = clock_mode()
    show_seconds()

    if mode == 'day':
        draw_pattern(colors['pattern'])
        return True

    if mode == 'night':
        hr = mn = dot = NIGHT_COLOR
    else:
        hr = mn = dot = sunset_color()

    if (digit_hours(0) > 0):
        number(hr[0],hr[1],hr[2],0,1,2,3,4,5,6,digit_hours(0))
    elif (digit_hours(0) == 0):
        pixels[0] = (0,0,0)
        pixels[1] = (0,0,0)
        pixels[2] = (0,0,0)
        pixels[3] = (0,0,0)
        pixels[4] = (0,0,0)
        pixels[5] = (0,0,0)
        pixels[6] = (0,0,0)

    number(hr[0],hr[1],hr[2],8,9,10,11,12,13,14,digit_hours(1))
    number(mn[0],mn[1],mn[2],16,17,18,19,20,21,22,digit_minutes(0))
    number(mn[0],mn[1],mn[2],24,25,26,27,28,29,30,digit_minutes(1))

    if mode == 'night':
        night_dot(digit_seconds())
    else:
        dots(dot[0],dot[1],dot[2],digit_seconds())
    return True


def main():
    """runs the clock until the Pi is switched off with the button."""
    while loop_once():
        pass



def destroy():
    """Stuff I don't realy understand"""
    GPIO.cleanup()

if __name__ == '__main__':
        setup()
        try:

            main()

#            c.close()
#            GPIO.cleanup()

        except:
            """writes down what went wrong, so it can be found later"""
            try:
                with open('/home/pi/timepi_error.log', 'a') as f:
                    f.write(str(datetime.now()) + '\n' + traceback.format_exc() + '\n')
            except Exception:
                pass
            destroy()
            pass

