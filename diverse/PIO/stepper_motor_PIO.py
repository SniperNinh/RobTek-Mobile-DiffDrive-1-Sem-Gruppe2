from machine import Pin
from rp2 import PIO, StateMachine, asm_pio
from time import sleep, tick_us, ticks_diff

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
clock_cycles_per_PWM = 5

# by defining 'set_init' to a tupple with 4 entries we tell the 
# statemachine running the program that we are working with 4 pins
@asm_pio(set_init=(PIO.OUT_LOW, PIO.OUT_LOW, PIO.OUT_LOW, PIO.OUT_LOW))
def PIO_set_step():

    pwm_high = 0
    pwm_low = 2

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

        self.pwm_pct = pwm_pct
        self.DEBUG_max_pwm_pct = DEBUG_max_pwm_pct

        self._sm = StateMachine(sm_id, PIO_set_step, freq=self.pwm_freq * clock_cycles_per_PWM, set_base=Pin(base_pin))

        self.update_sm_pwm_repeats(100)
        self.update_sm_direction("forward")

        self.outputs = [PWM(Pin(p + base_pin, Pin.OUT)) for p in range(4)] # laver min pwm pin outputs   
        for output in self.outputs: #sætter frekvensen på mine pins
            output.freq(frequency)

        self.current_step = 0
        self.current_step_count = 0
        self.current_steps_goal = 0
        self.currently_moving_stepper = False
        self.last_step_tick = tick_us()

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

    def update_sm_pwm_delay(self, new_delay):
        if isinstance(new_delay, float):
            raise ValueError("delay must be a float")

        self.pwm_repeats = int((1/self.pwm_freq) * new_delay)
        
        self._sm.put(self.pwm_repeats)  # we add the pwm_repeats value to the fifo-queue
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

    def rotate_coninuously(self, direction, delay):
        self.update_sm_direction(direction)

        self.update_sm_pwm_repeats(delay)

        self._sm.active(1)

    def set_step(self, step, pwm_pct=None):
        if pwm_pct != None and not isinstance(pwm_pct, float):
            raise ValueError("pwm_pct defined as a not float")

        elif isinstance(pwm_pct, float):
            if pwm_pct < 0 or pwm_pct > self.DEBUG_max_pwm_pct:
                raise ValueError("pwm_pct must be between 0 and 0.20")
            else:
                self.pwm_pct = pwm_pct

        for output, duty in zip(self.outputs, step): # sender en tilstand ud til de 4 pins
            output.duty_u16(int(self.pwm_pct * duty * 65535)) # omregner fra 0-1 til 16 bit dutycycle

    def move_stepper(self):
        ## moves the motor through the current set sequence until its goal is reached

        # lock_motor makes the motor reset the last step with a lower pwm_pct to avoid momentum
        if not self.currently_moving_stepper: return
        current_tick_us = tick_us
        if ticks_diff(current_tick_us, self.last_step_tick) < self.delay: return
        self.last_step_tick = current_tick_us
        
        self.current_step += 1
        if self.current_step >= len(self.current_sequence):
            self.current_step = 0
            self.current_step_count += 1

        self.set_step(self.current_sequence[self.current_step])

        if self.current_step_count >= self.current_steps_goal:
            print(f"{self} is done moving stepper")
            self.currently_moving_stepper = False


        # check if we are in a move_steps sequence
        # if no, then print "im done" once, and 
        # if yes, then set the correct step
        pass

    def generate_microstep_sequence(self, microsteps):
        """Generate and return a complete microstep sequence."""
        
        if not isinstance(microsteps, int) or microsteps < 4:
            raise ValueError("microsteps must be a positive integer higher than 3")
        
        sequence = []
        for step in range(microsteps * 4):
            sequence.append([max(0, math.sin(math.pi * 2 * (step + i*microsteps)/(microsteps/4))) for i in [1, 0, 3, 2]])
        
        return sequence

    def start_move_steps(self, steps, delay, step_mode, microsteps=None, direction="forward"):
        if self._sm.active():               raise ValueError("PIO is still running")

        if not isinstance(steps, int):  raise ValueError("sequences must be a integer")

        if not isinstance(delay, float):    raise ValueError("delay must be a float")
        elif delay < 0.001:                 raise ValueError("delay cant be less than 0.001s")

        if step_mode not in ("full", "half", "microstep"):                 raise ValueError('step_mode must be either "full" "half" or "microstep"')
        elif step_mode == "microstep" and not isinstance(microsteps, int): raise ValueError('set_mode is set to "microsteps" microsteps is not a integer')

        if direction not in ("forward", "backward"): raise ValueError("Direction needs to be forward or backward")

        if step_mode in ("full", "half"):
            self.current_sequence = self.modes(step_mode)
        else:
            self.current_sequence = self.generate_microstep_sequence(microsteps)

        if direction == "backward":
            self.current_sequence.reverse()
        
        self.delay = delay

        self.current_step = 0
        self.current_step_count = 0
        self.current_steps_goal = steps
        self.currently_moving_stepper = True

    def stop(self):
        self._sm.active(0)
        self._sm.exec("set(pins, 0b0000)") # we set all the pins to be low through the statemachine
        self.currently_moving_stepper = False
        self.set_step([0, 0, 0, 0])


PIO_stepper = StepperMotorPIO(base_pin=4)
try:
    PIO_stepper.rotate_coninuously("forward", 0.001)
    while True:
        pass

except:
    PIO_stepper.stop()