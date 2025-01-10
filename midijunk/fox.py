# this is a CircuitPython port of the fox code from rot13labs
# Copyright: 2024 Bradan Lane STUDIO

"""
/*
 *   Much of this code was copied from / inspired by Yet Another Foxbox
 *   (YAFB) by Gregory Stoike (KN4CK) which can be found here:
 *   https://github.com/N8HR/YAFB. It has been stripped down and adapted
 *   for use on a Seeed Studio XIAO ESP32C3 and a NiceRF SA868. All credit
 *   for this project goes to Gregory Stoike; I just made his work simple
 *   enough for my own simple foxes.
 *      
 *   This project is free software: you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as published by
 *   the Free Software Foundation, either version 3 of the License, or
 *   (at your option) any later version.
 *
 *   This project is distributed in the hope that it will be useful, but
 *   WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 *   General Public License for more details.
 *
 *   You should have received a copy of the GNU General Public License
 *   along with this. If not, see <https://www.gnu.org/licenses/>.
 */
"""

'''
    The rot13labs 2023 Fox Hunt Badge used the SA868 modem to transmit.
    The model is also capable of receive (but that capability is not used).
    
    The SA868 is a 2W UHF transceiver that operates in the
    2 meter and 440 MHz bands.     
    
    The code uses the lowe power output configuration: 45 mA and 25dBm.
    
    Communications between the Seeed ESP32C3 and the SA868 are done via UART
    at 9600 baud.
'''

import time
import math
import board
import busio
import digitalio
import pwmio


callmessage = "VE6MOG/W4 DECOY DECOY VE6MOG/W4"	#; // your callsign goes here
frequency = 146.565			#; // 146.565 is the normal TX frequency for foxes
transmit_delay = 30000		#; // delay between transmissions in milliseconds
bandwidth = 1				#; // Bandwidth, 0=12.5k, 1=25K
squelch = 3					#; // Squelch 0-8, 0 is listen/open
volume = 5					#; // Volume 1-8

PTT_Pin = board.D3			# // GPIO05 | D3 on XIAO
PD_Pin = board.D4			# // GPIO06 | D4 on XIAO
HL_Pin = board.D5			# // GPIO07 | D5 on XIAO
RX_Pin = board.D7 			# // GPIO20 | D7 on XIAO
TX_Pin = board.D6			# // GPIO21 | D6 on XIAO
MIC_Pin = board.D1			# // GPOI03 | D1 on XIAO

morse_map = {
    'a': ".-",
    'b': "-...",
    'c': "-.-.",
    'd': "-..",
    'e': ".",
    'f': "..-.",
    'g': "--.",
    'h': "....",
    'i': "..",
    'j': ".---",
    'k': "-.-",
    'l': ".-..",
    'm': "--",
    'n': "-.",
    'o': "---",
    'p': ".--.",
    'q': "--.-",
    'r': ".-.",
    's': "...",
    't': "-",
    'u': "..-",
    'v': "...-",
    'w': ".--",
    'x': "-..-",
    'y': "-.--",
    'z': "--..", 
    '0': "-----",
    '1': ".----",
    '2': "..---",
    '3': "...--",
    '4': "....-",
    '5': ".....",
    '6': "-....",
    '7': "--...",
    '8': "---..",
    '9': "----.",
    '.': ".-.-.-",
    ',': "--..--",
    '?': "..--..",
    "'": ".----.",
    '!': "-.-.--",
    '/': "-..-.",
    '(': "-.--.",
    ')': "-.--.-",
    '&': ".-...",
    ':': "---...",
    ';': "-.-.-.",
    '=': "-...-",
    '+': ".-.-.",
    '-': "-....-",
    '_': "..--.-",
    '"': ".-..-.",
    '$': "...-..-",
    '@': ".--.-."
}

# each tuple is a midi note number and the number of 32nd-ths duration: 2/32 = 16th, 8/32 = 1/4, 32/32 = whole, etc
# a dotted note is 1.5 times the duration
midi_music = [
  (69,2), (71,2), (74,2), (71,2), (78,6), (78,6), (76,12),
  (69,2), (71,2), (74,2), (71,2), (76,6), (76,6), (74,6), 
  (73,2), (71,6), (69,2), (71,2), (74,2), (71,2),
  (74,8), (76,4), (73,6), (71,2), (69,4), (69,4), (69,4), 
  (76,8), (74,16), (69,2), (71,2), (74,2), (71,2),
  (78,6), (78,6), (76,12), (69,2), (71,2), (74,2), (71,2),
  (81,8), (73,4), (74,6), (73,2), (71,4), (69,2), (71,2), (74,2), (71,2),
  (74,8), (76,4), (73,6), (71,2), (69,8), (69,4), (76,8), (74,16), (0,8)
]

o_canada_melody = [
    (79, 8), (82, 4), (0, 2), (82, 2), (75, 12), (77, 4), (79, 4),
    (80, 4), (82, 4), (84, 4), (77, 12), (0, 4), (79, 8), (81, 4),
    (0, 2), (81, 2), (82, 12), (84, 4), (86, 4), (86, 4), (84, 4),
    (84, 4), (82, 12), (77, 3), (79, 1), (80, 6), (79, 2), (77, 4),
    (79, 3), (80, 1), (82, 6), (80, 2), (79, 4), (80, 3), (82, 1),
    (84, 4), (82, 4), (80, 4), (79, 4), (77, 12), (77, 3), (79, 1),
    (80, 6), (79, 2), (77, 4), (79, 3), (80, 1), (82, 6), (80, 2),
    (79, 4), (79, 4), (77, 4), (82, 4), (82, 2), (81, 2), (79, 2),
    (81, 2), (82, 8), (0, 8), (79, 8), (82, 6), (82, 2), (75, 8),
    (0, 8), (80, 8), (84, 4), (0, 2), (84, 2), (77, 8), (0, 8),
    (82, 8), (83, 4), (0, 2), (83, 2), (84, 4), (80, 4), (79, 4),
    (77, 4), (75, 8), (77, 8), (79, 8), (0, 8), (82, 8), (87, 4),
    (0, 2), (87, 2), (84, 4), (80, 4), (79, 4), (77, 4), (82, 8),
    (74, 8), (75, 16),
]

topgun_melody = [
    (0, 4), (61, 8), (68, 8), (68, 8), (66, 4), (65, 4), (66, 4),
    (65, 4), (63, 8), (63, 8), (61, 4), (63, 4), (65, 8), (63, 4),
    (65, 4), (66, 8), (65, 4), (61, 4), (65, 8), (63, 32), (61, 8),
    (68, 8), (68, 8), (66, 4), (65, 4), (66, 4), (65, 4), (63, 8),
    (63, 8), (61, 4), (63, 4), (65, 8), (63, 4), (65, 4), (66, 8),
    (65, 4), (61, 4), (68, 32),
]


god_save_the_king = [
    (91, 8), (91, 8), (93, 8), (90, 12), (91, 4), (93, 8), (95, 8),
    (95, 8), (96, 8), (95, 12), (93, 4), (91, 8), (93, 8), (91, 8),
    (90, 8), (91, 8),
]

final_countdown = [
    (0, 8), (0, 4), (83, 2), (81, 2), (83, 8), (76, 8), (0, 8),
    (0, 4), (84, 2), (83, 2), (84, 4), (83, 4), (81, 8), (0, 8),
    (0, 4), (84, 2), (83, 2), (84, 8), (76, 8), (0, 8), (0, 4),
    (81, 2), (79, 2), (81, 4), (79, 4), (78, 4), (81, 4), (79, 12),
    (78, 2), (79, 2), (81, 12), (79, 2), (81, 2), (83, 4), (81, 4),
    (79, 4), (78, 4), (76, 8), (84, 8), (83, 24), (83, 2), (84, 2),
    (83, 2), (81, 2), (83, 32),
]

wannabe_melody = [
    (79, 2), (79, 2), (79, 2), (79, 2), (79, 4), (81, 4), (79, 4),
    (76, 4), (0, 4),   (72, 2), (74, 2), (72, 2), (74, 4), (74, 4),
    (72, 4), (76, 8), (0, 8),   (79, 4), (79, 4), (79, 4), (81, 4),
    (79, 4), (76, 4), (0, 4),   (84, 8), (84, 4), (83, 4), (79, 4),
    (81, 4), (83, 2), (81, 2), (79, 8),
]



def init_pin(pin, default=False):
    rtn = digitalio.DigitalInOut(pin)
    rtn.direction = digitalio.Direction.OUTPUT
    rtn.value = default
    return rtn
    
def delay(ms):
    seconds = ms / 1000
    #print(f"delay for {seconds:.2f} seconds")
    time.sleep(seconds)

def serial_out(message, ms=100):
    global uart
    #print(f"sending command:   '{message}'")
    uart.write(bytes(f"{message}\r\n", 'ascii'))
    delay(ms)
    response = uart.read(64)
    if not response:
        print(f"no response to '{message}'")
    else:
        #print(f"received response: '{response.decode().strip()}'")
        pass

sound_pwm = None

def tone_on(frequency:float=440.0):
    global mic, sound_pwm
    ''' produce the given sound for the given amount of time '''
    #print(f"Tone On ({frequency:f})")
    frequency = int(frequency)
    if mic:
        mic.deinit()
        mic = None
    # create the pwm ourput if it doesn't exist; otherwise, just change the frequency
    if not sound_pwm:
        sound_pwm = pwmio.PWMOut(MIC_Pin, frequency=frequency, variable_frequency=True)
        sound_pwm.duty_cycle = (65535 // 2) #0x8000
    else:
        sound_pwm.frequency = frequency

def tone_off():
    global mic, sound_pwm
    ''' stop producing sound '''
    #print("Tone Off")
    if sound_pwm:
        sound_pwm.deinit()
        sound_pwm = None
    mic = init_pin(MIC_Pin, False)
    
def tone(frequency:float=440.0, duration:int=0.5):
    tone_on(frequency)
    delay(duration)
    tone_off()

def midi_to_frequency(note:int):
    ''' convert a note to a frequency '''
    return 440.0 * (2 ** ((note - 69) / 12.0))

def frequency_to_midi(frequency:float):
    ''' convert a frequency to a note '''
    return 69 + (12 * (math.log(frequency / 440.0) / math.log(2)))

def play_midi_song():
    global midi_music
    print(f"playing music: ", end='')
    TEMP = 140
    THIRTYSECOND = 60000 * 5 // (TEMP * 32)
    
    for note, duration in midi_music:
        if note == 0:
            delay(duration * THIRTYSECOND)
        else:
            tone(midi_to_frequency(note), (duration * THIRTYSECOND))
            
def play_o_canada():
    global o_canada_melody
    print(f"playing music: ", end='')
    TEMP = 140
    THIRTYSECOND = 60000 * 5 // (TEMP * 32)
    
    for note, duration in o_canada_melody:
        if note == 0:
            delay(duration * THIRTYSECOND)
        else:
            tone(midi_to_frequency(note), (duration * THIRTYSECOND))
            
def play_topgun():
    global topgun_melody
    print(f"playing music: ", end='')
    TEMP = 140
    THIRTYSECOND = 60000 * 5 // (TEMP * 32)
    
    for note, duration in topgun_melody:
        if note == 0:
            delay(duration * THIRTYSECOND)
        else:
            tone(midi_to_frequency(note), (duration * THIRTYSECOND))
            
def play_finalcountdown():
    global final_countdown
    print(f"playing music: ", end='')
    TEMP = 140
    THIRTYSECOND = 60000 * 5 // (TEMP * 32)
    
    for note, duration in final_countdown:
        if note == 0:
            delay(duration * THIRTYSECOND)
        else:
            tone(midi_to_frequency(note), (duration * THIRTYSECOND))
            
def play_wannabe():
    global wannabe_melody
    print(f"playing music: ", end='')
    TEMP = 140
    THIRTYSECOND = 60000 * 5 // (TEMP * 32)
    
    for note, duration in wannabe_melody:
        if note == 0:
            delay(duration * THIRTYSECOND)
        else:
            tone(midi_to_frequency(note), (duration * THIRTYSECOND))
            
def play_god_save_the_king():
    global god_Save_the_king
    print(f"playing music: ", end='')
    TEMP = 140
    THIRTYSECOND = 60000 * 5 // (TEMP * 32)
    
    for note, duration in god_save_the_king:
        if note == 0:
            delay(duration * THIRTYSECOND)
        else:
            tone(midi_to_frequency(note), (duration * THIRTYSECOND))

def play_morse(message=callmessage):
    '''
    /*
       * short mark, dot or "dit" (.): "dot duration" is one time unit long      
       * longer mark, dash or "dah" (-): three time units long
       * inter-element gap between the dots and dashes within a character: one dot duration or one unit long
       * short gap (between letters): three time units long      
       * medium gap (between words): seven time units long
    */
    '''
    print(f"transmitting '{message}': ", end='')
    
    WPM = 12
    TONE = 800
    DURATION = 60000 / (WPM*50)
    
    for c in message:
        if c == ' ':
            delay(DURATION*(7-3))	# we already delayed 3 after the character
            print(' // ',end='')
            continue
        
        c = c.lower()
        morse = morse_map.get(c, None)
        if morse == None:
            continue

        print(morse, end='')
        for mark in morse:
            if mark == '.':
                tone(TONE, DURATION)
            else: # == '-'
                tone(TONE, DURATION*3)
            delay(DURATION)
            
        delay(DURATION*(3-1))		# we already delayed 1 after the last mark
        print(' ', end='')
    print()





# begin executing code for setup

print("initializing system ... ", end='')

uart = busio.UART(TX_Pin, RX_Pin, baudrate=9600, timeout=1.0)
delay(1000)

#print("setting up PTT, Power Down, Power Level, MIC")

ptt = init_pin(PTT_Pin, True)
pd = init_pin(PD_Pin, True)
power = init_pin(HL_Pin, False)
mic = init_pin(MIC_Pin, False)

#print("initializing modem")
serial_out("AT+DMOCONNECT", ms=500)

#print("initializing frequency")
message = f"AT+DMOSETGROUP={bandwidth:d},{frequency:.4f},{frequency:.4f},0000,{squelch:d},0000"
serial_out(message)

#print("initializing volume")
volume = 8 if volume > 8 else volume
message = f"AT+DMOSETVOLUME={volume:d}"
serial_out(message)

print("ready")



# user should have changed the default callsign
if callmessage == "Fox Hunt":
    print(f"** WARNING **  callsign has not been set. Current callsign is '{callmessage}'")

# Songs in my loop
songs = [
    play_midi_song,
    play_o_canada,
    play_topgun,
    play_finalcountdown,
    play_wannabe,
    play_god_save_the_king
]

# We'll keep an index to track which function to call
song_index = 0

# begin main loop

while True:
    ptt.value = False 		# begin transmit
    
    # commented out the callsign, don't tell the FCC
    delay(750)
    play_morse()        # transmit the global 'callmessage'

    # playing o canada because I can
    delay(750)
    # --- Call the next function in the list ---
    songs[song_index]()  
    # ------------------------------------------
    
    ptt.value = True 		# Put the SA868 in RX mode
    
    delay(transmit_delay)	# wait before next transmission
    
    # Move to the next function; wrap around using modulo
    song_index = (song_index + 1) % len(songs)

