import math
from machine import Pin, PWM
from time import sleep
from diff_drive import DifferentialDrive

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
            "half": [
                [self.v, 0, 0, 0],
                [self.v * 0.7071, self.v * 0.7071, 0, 0],
                [0, self.v, 0, 0],
                [0, self.v * 0.7071, self.v * 0.7071, 0],
                [0, 0, self.v, 0],
                [0, 0, self.v * 0.7071, self.v * 0.7071],
                [0, 0, 0, self.v],
                [self.v * 0.7071, 0, 0, self.v * 0.7071],
            ],
        }
        
        for mode in self.modes:
            self.modes[mode] = [
                [int(value * 65535) for value in phase]
                for phase in self.modes[mode]
    ]
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
            output.duty_u16(duty)

    def stop(self):
        self.set_step([0, 0, 0, 0]) # slukker alle 4 outputs

