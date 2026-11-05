from machine import Pin, PWM
from rp2 import PIO, StateMachine, asm_pio
from time import sleep, ticks_us, ticks_diff
import math


# start i python hvis man lige vil forstå hvad der foregår


# in our program we use the isr (input-shift-register) to store our pwm_repeats value
# and we use the osr (output-shift-register) to store our pwm_delay value
# we then move the values into the y and x registers to work as countdowns

"""
each step essentially works like this;

y = isr
while y != 0:
    x = osr
    set(pins, 0b1100)
    while x != 0:
        x -= 1
    set(pins, 0b0000)
    y -= 1
"""

# This value is hardcoded, its equal to pwm_high + pwm_low + 3
# If this value is off the calculated frequencies by the class cant be trusted
clock_cycles_per_PWM = 40

# by defining 'set_init' to a tupple with 4 entries we tell the 
# statemachine running the program that we are working with 4 pins
@asm_pio(set_init=(PIO.OUT_LOW, PIO.OUT_LOW, PIO.OUT_LOW, PIO.OUT_LOW))
def PIO_set_step():

    pwm_high = 7
    pwm_low = 30

    mov(y, isr)   # we are copying the pwm_repeats value in the isr into the y-register
    wrap_target() # when the program hits 'wrap()' it returns here without using a cycle, kinda like a 'while True'

    label("step_0")
    set(pins, 0b1100) [pwm_high]
    set(pins, 0b0000) [pwm_low]
    jmp(y_dec, "step_0")    # if y != 0, go run the code after the 'label("step_0")' and decrement y (after checking its value)
    mov(y, isr)
    jmp(not_x, "step_3")

    label("step_1")
    set(pins, 0b0110) [pwm_high]
    set(pins, 0b0000) [pwm_low]
    jmp(y_dec, "step_1")
    mov(y, isr)
    jmp(not_x, "step_0")

    label("step_2")
    set(pins, 0b0011) [pwm_high]
    set(pins, 0b0000) [pwm_low]
    jmp(y_dec, "step_2")
    mov(y, isr)
    jmp(not_x, "step_1")

    label("step_3")
    set(pins, 0b1001) [pwm_high]
    set(pins, 0b0000) [pwm_low]
    jmp(y_dec, "step_3")
    mov(y, isr)
    jmp(not_x, "step_2")

    wrap()


class StepperMotorPIO:
    def __init__(self, base_pin, sm_id=0, pwm_freq=22_000, pwm_pct=0.2, DEBUG_max_pwm_pct=0.2):
        # base_pin is the first pin in a sequence of 4, aka if base_pin=16, the motor will use pins (16, 17, 18, 19)
        # sm_id is what statemachine we'll use
        # pwm_freq is used to calculate the statemachines frequency using the amount of clock cycles there is per PWM high-low signal
        # pwm_pct is only for the python pwm
        self.pwm_freq = pwm_freq

        self._sm = StateMachine(sm_id, PIO_set_step, freq=self.pwm_freq * clock_cycles_per_PWM, set_base=Pin(base_pin))
        self._sm_id = sm_id

        self.base_pin = base_pin

        self.pwm_pct = pwm_pct
        self.DEBUG_max_pwm_pct = DEBUG_max_pwm_pct

        self._define_PWM_outputs()
        
        self.current_step = 0
        self.current_step_count = 0
        self.current_steps_goal = 0
        self.currently_moving_stepper = False
        self.last_step_tick = ticks_us()

        self.modes = {
            "full": [ # full step: to spoler tændt ad gangen
                [1, 1, 0, 0],
                [0, 1, 1, 0],
                [0, 0, 1, 1],
                [1, 0, 0, 1],
            ],
            "half": [ # half step: skiftevis en og to spoler tændt
                [1, 0, 0, 0],
                [1, 1, 0, 0],
                [0, 1, 0, 0],
                [0, 1, 1, 0],
                [0, 0, 1, 0],
                [0, 0, 1, 1],
                [0, 0, 0, 1],
                [1, 0, 0, 1],
            ], 
        }
    
    def _define_PWM_outputs(self):
        if self._sm.active():
            self._sm.active(0)
            print(ValueError("statemachine has been deactivated while defining PWM outputs"))

        self.outputs = [PWM(Pin(p + self.base_pin, Pin.OUT)) for p in range(4)] # laver min pwm pin outputs   
        for output in self.outputs: #sætter frekvensen på mine pins
            output.freq(self.pwm_freq)

    def update_sm_pwm_delay(self, new_delay):
        if not isinstance(new_delay, float):
            raise ValueError("delay must be a float")
        pwm_repeats = math.ceil(self.pwm_freq * new_delay)
        print("pwm_repeats:", pwm_repeats, " actual delay:", pwm_repeats/self.pwm_freq)
        self._sm.put(pwm_repeats)  # we add the pwm_repeats value to the fifo-queue
        self._sm.exec("pull()")         # we make the statemachine move the pwm-repeats value into the osr
        self._sm.exec("mov(isr, osr)")  # and we copy it into the isr where the pwm_repeats value lives

    def update_sm_direction(self, new_direction):
        if new_direction == "forward":
            self.pio_direction = 0
        elif new_direction == "backward":
            self.pio_direction = 1
        else:
            raise ValueError("Direction needs to be forward or backward, direction not changed in PIO")
        self._sm.put(self.pio_direction)
        self._sm.exec("pull()")
        self._sm.exec("mov(x, osr)")

    def setup_PIO(self, direction, delay):
        self._sm = StateMachine(self._sm_id, PIO_set_step, freq=self.pwm_freq * clock_cycles_per_PWM, set_base=Pin(self.base_pin))

        self.update_sm_pwm_delay(delay)
        self.update_sm_direction(direction)

    def start_sm(self):
        self._sm.active(1)

    def set_step(self, step, override_pwm_pct=None):
        if self._sm.active():
            raise ValueError("cannot set step while PIO is running")
        active_pwm_pct = self.pwm_pct
        if override_pwm_pct != None and not isinstance(override_pwm_pct, float):
            raise ValueError("override_pwm_pct defined as a not float")
        elif isinstance(override_pwm_pct, float):
            if override_pwm_pct < 0 or override_pwm_pct > self.DEBUG_max_pwm_pct:
                raise ValueError(f"override_pwm_pct must be between 0 and {self.DEBUG_max_pwm_pct}")
            else:
                active_pwm_pct = override_pwm_pct

        for output, duty in zip(self.outputs, step): # sender en tilstand ud til de 4 pins
            output.duty_u16(int(active_pwm_pct * duty * 65535)) # omregner fra 0-1 til 16 bit dutycycle

    def move_stepper(self):
        ## moves the motor through the current set sequence until its goal is reached
        if not self.currently_moving_stepper: return
        current_tick_us = ticks_us()
        if ticks_diff(current_tick_us, self.last_step_tick) < (self.delay * 1_000_000): return
        self.last_step_tick = current_tick_us
        
        self.current_step += 1
        self.current_step %= len(self.current_sequence)
        if self.current_step <= 0:
            self.current_step_count += 1

        self.set_step(self.current_sequence[self.current_step])

        if self.current_step_count >= self.current_steps_goal:
            self.currently_moving_stepper = False

    def generate_microstep_sequence(self, microsteps):
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
            row[pin_fading_in] = math.cos(angle) # cos fader ned fra fuld styrke
            row[pin_fading_out] = math.sin(angle) # sin fader op mod næste pin
            
            sequence.append(row) # gemmer tilstanden i listen
        return sequence

    def start_move_sequences(self, sequences, delay, step_mode, microsteps=None, direction="forward"):
        if self._sm.active():               raise ValueError("PIO is still running")

        if not isinstance(sequences, int):  raise ValueError("sequences must be a integer")

        if not isinstance(delay, float):    raise ValueError("delay must be a float")
        elif delay < 0.001:                 raise ValueError("delay cant be less than 0.001s")

        if step_mode not in ("full", "half", "microstep"):                 raise ValueError('step_mode must be either "full" "half" or "microstep"')
        elif step_mode == "microstep" and not isinstance(microsteps, int): raise ValueError('set_mode is set to "microsteps" microsteps is not a integer')

        if direction not in ("forward", "backward"): raise ValueError("Direction needs to be forward or backward")

        if step_mode in ("full", "half"):
            self.current_sequence = self.modes[step_mode]
        else:
            self.current_sequence = self.generate_microstep_sequence(microsteps)
            print(self.current_sequence)

        if direction == "backward":
            self.current_sequence.reverse()
        
        self._define_PWM_outputs()

        self.delay = delay

        self.current_step = 0
        self.current_step_count = 0
        self.current_steps_goal = sequences * len(self.current_sequence)
        self.currently_moving_stepper = True
    
    def lock_motor(self):
        if self._sm.active():
            raise ValueError("attempted to lock motor with sm still active")
        
        self._define_PWM_outputs()
        self.currently_moving_stepper = False
        if not isinstance(self.current_sequence, list):
            self.set_step([1, 1, 0, 0])
        else:
            self.set_step(self.current_sequence[self.current_step])

    def stop(self):
        self._sm.active(0)
        self._sm.exec("set(pins, 0b0000)") # we set all the pins to be low through the statemachine
        self.currently_moving_stepper = False
        self.set_step([0, 0, 0, 0])
