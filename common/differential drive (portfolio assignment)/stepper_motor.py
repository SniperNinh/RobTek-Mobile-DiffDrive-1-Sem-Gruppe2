import math
from machine import Pin, PWM
from time import sleep

class StepperMotor:
    def __init__(self, pins, pwm_pct=0.5, frequency=18_000):
        self.total_steps = 0 # counter til at vise hvor mange steps er forekommet
        self.outputs = [PWM(Pin(p, Pin.OUT)) for p in pins] # laver min pwm pin outputs   
        for o in self.outputs: #sætter frekvensen på mine pins
            o.freq(frequency)

        self.v = pwm_pct # sætter dutycycle
        self.modes = {
            "full": [ # full step: to spoler tændt ad gangen
                [self.v, self.v, 0, 0],
                [0, self.v, self.v, 0],
                [0, 0, self.v, self.v],
                [self.v, 0, 0, self.v],
            ],
            "half": [ # half step: skiftevis en og to spoler tændt
                [self.v, 0, 0, 0],
                [self.v, self.v, 0, 0],
                [0, self.v, 0, 0],
                [0, self.v, self.v, 0],
                [0, 0, self.v, 0],
                [0, 0, self.v, self.v],
                [0, 0, 0, self.v],
                [self.v, 0, 0, self.v],
            ], 
        }
        self.mode = "full" # standard mode hvis man ikke vælger en
        self.stop() # starter med alle outputs slukket

    def generate_microstep(self, microsteps):
        """microsteps = antallet af små steps et fuldt step bliver fordelt ud i.
        cos/sin fading sørger for at torque ikke variere.
        """
        if not isinstance(microsteps, int) or microsteps < 1: # kun positive hele tal er gyldige
            raise ValueError("microsteps must be a positive integer")
        sequence = [] # her samles alle microstep tilstande
        n = 4 * microsteps # 4 fulde steps i en hel cyklus gange antal microsteps                              
        for k in range(n):
            quadrant = k // microsteps # hvilket af de 4 fulde steps vi er i
            angle = (math.pi/2) * (k % microsteps/microsteps) # hvor langt vi er i det fulde step (0 til 90 grader)

            pin_fading_in = quadrant # pin der fader ind
            pin_fading_out = (quadrant + 1) % 4 # næste pin, % 4 sørger for at den hopper rundt til 0

            row = [0.0,0.0,0.0,0.0] # alle pins starter på 0
            row[pin_fading_in] = math.cos(angle) * self.v # cos fader ned fra fuld styrke
            row[pin_fading_out] = math.sin(angle) * self.v # sin fader op mod næste pin
            
            sequence.append(row) # gemmer tilstanden i listen
        return sequence

    def set_step_mode(self, mode, microsteps=None): 
        if mode == "microstep":
            self.modes["microstep"] = self.generate_microstep(microsteps) # laver listen og gemmer den sammen med de andre modes
        elif mode not in self.modes:
            raise ValueError("mode must be 'full', 'half' or 'microstep'") # fejl hvis navnet er forkert
        self.mode = mode # gemmer navnet på den valgte mode                      
        self.microstep = microsteps # gemmer antal microsteps

    def set_step(self, step):
        for output, duty in zip(self.outputs, step): # sender en tilstand ud til de 4 pins
            output.duty_u16(int(duty * 65535)) # omregner fra 0-1 til 16 bit dutycycle

    def stop(self):
        self.set_step([0, 0, 0, 0]) # slukker alle 4 outputs

    def rotate_full_step(self, steps, delay, direction="forward", continuous=False):
        
        if direction not in ("forward", "backward"):
            raise ValueError("direction must be 'forward' or 'backward'") # fejl hvis retningen er forkert

        delay = max(delay, 0.001) # delay kan ikke blive hurtigere end 1 ms

        change = 1 # forward tæller total_steps op
        sequence = self.modes[self.mode] # henter listen for den valgte mode
        if direction == "backward":
            sequence = sequence[::-1] # vender listen om så motoren drejer den anden vej
            change = -1 # backward tæller total_steps ned

        try:
            stop_button = Pin(27, Pin.IN, Pin.PULL_UP) # stop knap, er 0 når den trykkes  
            if continuous:
                while  stop_button.value() != 0: # kører indtil knappen trykkes
                    for step in sequence:
                        self.set_step(step) # sender tilstanden til motoren
                        sleep(delay) # venter mellem hvert step
                        self.total_steps += change # opdaterer positionen
            else:
                    for _ in range(abs(steps)): # negative steps bruges som positive, retningen styres af direction
                        if stop_button.value() == False:
                            break # stopper hvis knappen trykkes
                        for step in sequence:
                            self.set_step(step)
                            sleep(delay)
                            self.total_steps += change
        finally:
            self.stop() # slukker altid outputs, også ved fejl eller afbrydelse