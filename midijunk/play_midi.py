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
