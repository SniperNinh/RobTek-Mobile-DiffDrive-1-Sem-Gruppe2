from machine import Pin, PWM
from rp2 import PIO, StateMachine, asm_pio
from time import ticks_us, ticks_diff
import math
import gc
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

# This value is hardcoded, its equal to pwm_high + 1
# If this value is off, the calculated frequencies by the class cant be trusted
pwm_high_total = 32

# by defining 'set_init' to a tupple with 4 entries we tell the 
# statemachine running the program that we are working with 4 pins
@asm_pio(set_init=(PIO.OUT_LOW, PIO.OUT_LOW, PIO.OUT_LOW, PIO.OUT_LOW))
def PIO_set_step():

    pwm_high = 31

    wrap_target() # when the program hits 'wrap()' it returns here without using a cycle, kinda like a 'while True'

    mov(y, isr)             # we are copying the value in the isr into the y-register
    label("step_0")
    mov(x, osr)             # we are copying the value in the osr into the x-register
    set(pins, 0b1100) [pwm_high]
    set(pins, 0b0000)
    label("pwm_0")
    jmp(x_dec, "pwm_0")    # if x != 0, go run the code after the 'label("pwm_0")' and decrement x (after checking its value)
    jmp(y_dec, "step_0")    # if y != 0, go run the code after the 'label("step_0")' and decrement y (after checking its value)

    mov(y, isr)
    label("step_1")
    mov(x, osr)
    set(pins, 0b0110) [pwm_high]
    set(pins, 0b0000)
    label("pwm_1")
    jmp(x_dec, "pwm_1")
    jmp(y_dec, "step_1")

    mov(y, isr)
    label("step_2")
    mov(x, osr)
    set(pins, 0b0011) [pwm_high]
    set(pins, 0b0000)
    label("pwm_2")
    jmp(x_dec, "pwm_2")
    jmp(y_dec, "step_2")

    mov(y, isr)
    label("step_3")
    mov(x, osr)
    set(pins, 0b1001) [pwm_high]
    set(pins, 0b0000)
    label("pwm_3")
    jmp(x_dec, "pwm_3")
    jmp(y_dec, "step_3")

    wrap()


class StepperMotorPIO:
    def __init__(self, base_pin, sm_id=0, pwm_freq=22_000, pwm_pct=0.2, DEBUG_max_pwm_pct=0.2):
        # base_pin is the first pin in a sequence of 4, aka if base_pin=16, the motor will use pins (16, 17, 18, 19)
        # sm_id is what statemachine we'll use
        # pwm_freq is used to calculate the statemachines frequency using the amount of clock cycles there is per PWM high-low signal
        # pwm_pct is only for the python pwm
        self.pwm_freq = pwm_freq
        self.clock_cycles_per_PWM = int(pwm_high_total/pwm_pct)

        self._sm = StateMachine(sm_id, PIO_set_step, freq=self.pwm_freq * self.clock_cycles_per_PWM, set_base=Pin(base_pin))
        self._sm_id = sm_id

        self.base_pin = base_pin

        self.pwm_pct = pwm_pct
        self.DEBUG_max_pwm_pct = DEBUG_max_pwm_pct

        self._define_PWM_outputs()
        
        self.current_step = 0
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
                [math.sqrt(0.5), math.sqrt(0.5), 0, 0],
                [0, 1, 0, 0],
                [0, math.sqrt(0.5), math.sqrt(0.5), 0],
                [0, 0, 1, 0],
                [0, 0, math.sqrt(0.5), math.sqrt(0.5)],
                [0, 0, 0, 1],
                [math.sqrt(0.5), 0, 0, math.sqrt(0.5)],
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

    def update_sm_pwm_pct(self, new_pwm_pct):
        if 0 > new_pwm_pct > self.DEBUG_max_pwm_pct: raise ValueError(f"delay must be between 0.001 and {self.DEBUG_max_pwm_pct}")
        self.pwm_pct = new_pwm_pct
        
        self._sm.put(int(32/self.pwm_pct - 32))
        self._sm.exec("pull()")
        self._sm.exec("mov(x, osr)")

    def setup_PIO(self, delay, pwm_pct):
        self._sm = StateMachine(self._sm_id, PIO_set_step, freq=self.pwm_freq * self.clock_cycles_per_PWM, set_base=Pin(self.base_pin))

        self.update_sm_pwm_delay(delay)
        self.update_sm_pwm_pct(pwm_pct)

    def start_sm(self):
        self._sm.active(1)

    def set_step(self, step):
        if self._sm.active():
            raise ValueError("cannot set step while PIO is running")
        for output, duty in zip(self.outputs, step): # sender en tilstand ud til de 4 pins
            output.duty_u16(duty) # omregner fra 0-1 til 16 bit dutycycle

    def move_stepper(self, run_gc=False):
        ## moves the motor through the current set sequence until its goal is reached
        if not self.currently_moving_stepper: return
        current_tick = ticks_us()
        if ticks_diff(current_tick, self.last_step_tick) < (self.delay * 1_000_000): return
        print(ticks_diff(current_tick, self.last_step_tick))
        
        self.current_step += 1

        self.set_step(self.current_sequence[self.current_step % len(self.current_sequence)])

        self.last_step_tick = current_tick
        if self.current_step >= self.current_steps_goal:
            self.currently_moving_stepper = False
        
        if run_gc: gc.collect()

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
        print(direction)
        if self._sm.active():                raise ValueError("PIO is still running")

        if not isinstance(sequences, int):   raise ValueError("sequences must be a integer")

        if not isinstance(delay, float):     raise ValueError("delay must be a float")
        elif delay < 0.001:                  raise ValueError("delay cant be less than 0.001s")
        elif delay > self.DEBUG_max_pwm_pct: raise ValueError(f"delay cant be bigger than {self.DEBUG_max_pwm_pct}")

        if step_mode not in ("full", "half", "microstep"):                 raise ValueError('step_mode must be either "full" "half" or "microstep"')
        elif step_mode == "microstep" and not isinstance(microsteps, int): raise ValueError('set_mode is set to "microsteps" microsteps is not a integer')

        if direction not in ("forward", "backward"): raise ValueError("Direction needs to be forward or backward")

        if step_mode in ("full", "half"):
            self.current_sequence = self.modes[step_mode]
        else:
            self.current_sequence = self.generate_microstep_sequence(microsteps)
            #print(self.current_sequence)

        if direction == "backward":
            self.current_sequence = self.current_sequence[::-1]
        

        self.current_sequence = [[int(i*(2**16-1)*self.pwm_pct) for i in step] for step in self.current_sequence]

        self._define_PWM_outputs()

        self.delay = delay
        print(delay, self.delay)

        self.current_step = 0
        self.current_steps_goal = sequences * len(self.current_sequence)
        self.currently_moving_stepper = True
    
    def lock_motor(self, lock_pwm_pct=0.04):
        if self._sm.active():
            raise ValueError("attempted to lock motor with sm still active")
        
        pwm_pct_uint16 = int((2**16-1)*lock_pwm_pct)

        self._define_PWM_outputs()
        self.currently_moving_stepper = False
        self.set_step([pwm_pct_uint16, pwm_pct_uint16, 0, 0])

    def stop(self):
        self._sm.active(0)
        self._sm.exec("set(pins, 0b0000)") # we set all the pins to be low through the statemachine
        self.currently_moving_stepper = False
        self.set_step([0, 0, 0, 0])
