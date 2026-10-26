from machine import Pin
from rp2 import PIO, StateMachine, asm_pio
from time import sleep

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

# by defining 'set_init' to a tupple with 4 entries we tell the 
# statemachine running the program that we are working with 4 pins
@asm_pio(set_init=(PIO.OUT_LOW, PIO.OUT_LOW, PIO.OUT_LOW, PIO.OUT_LOW))
def PIO_set_step():
    wrap_target() # when the program hits 'wrap()' it returns here without using a cycle, kinda like a 'while True'

    mov(y, isr)             # we are copying the value in the isr into the y-register
    label("step_0")
    mov(x, osr)             # we are copying the value in the osr into the x-register
    set(pins, 0b1100)
    label("pwm_0")
    jmp(x_dec, "pwm_0")    # if x != 0, go run the code after the 'label("pwm_0")' and decrement x (after checking its value)
    set(pins, 0b0000) [30]
    jmp(y_dec, "step_0")    # if y != 0, go run the code after the 'label("step_0")' and decrement y (after checking its value)

    mov(y, isr)
    label("step_1")
    mov(x, osr)
    set(pins, 0b0110)
    label("pwm_1")
    jmp(x_dec, "pwm_1")
    set(pins, 0b0000) [30]
    jmp(y_dec, "step_1")

    mov(y, isr)
    label("step_2")
    mov(x, osr)
    set(pins, 0b0011)
    label("pwm_2")
    jmp(x_dec, "pwm_2")
    set(pins, 0b0000) [30]
    jmp(y_dec, "step_2")

    mov(y, isr)
    label("step_3")
    mov(x, osr)
    set(pins, 0b1001)
    label("pwm_3")
    jmp(x_dec, "pwm_3")
    set(pins, 0b0000) [30]
    jmp(y_dec, "step_3")

    wrap()


class StepperMotorPIO:
    def __init__(self, base_pin, sm_id=0, sm_freq=2_160_000, pwm_delay=96, pwm_repeats=138):
        # base_pin is the first pin in a sequence of 4, aka if base_pin=16, the motor will use pins (16, 17, 18, 19)
        # sm_id is what statemachine we'll use
        # sm_freq is roughly the frequency the statemachine will use, although the actual frequency is gotten by clock-dividers which are limited in what frequencies they can produce
        # pwm_delay is how many clock_cycles -1 we spend in high, we spend 32 cycles in low
        # pwm_repeats is how many high-low cycles we do in each step in the full-step sequence

        self._sm = StateMachine(sm_id, PIO_set_step, freq=sm_freq, set_base=Pin(base_pin))
        
        self.update_delays(pwm_repeats, pwm_delay)
    
    def update_delays(self, new_pwm_repeats=None, new_pwm_delay=None): #we might need to turn off the statemachine while running this incase bugs happens where the sm reads the pwm_repeats as pwm_delay
        if new_step_repeats != None:
            self.pwm_repeats = new_pwm_repeats
        
        if new_pwm_delay != None:
            self.pwm_delay = new_pwm_delay

        self._sm.put(self.pwm_repeats)  # we add the pwm_repeats value to the fifo-queue
        self._sm.exec("pull()")         # we make the statemachine move the pwm-repeats value into the osr
        self._sm.exec("mov(isr, osr)")  # and we copy it into the isr where the pwm_repeats value lives

        self._sm.put(self.pwm_delay)    # we add the pwm_delay value into the fifo-queue
        self._sm.exec("pull()")         # we make the statemachine pull the pwm_delay into the osr where it lives
    
    def stop(self):
        self._sm.active(0)
        self._sm.exec("set(pins, 0b0000)") # we set all the pins to be low through the statemachine



try:
    PIO_stepper = StepperMotorPIO(base_pin=16)
    PIO_stepper._sm.active(1)
    while True:
        pass

except:
    PIO_stepper.stop()