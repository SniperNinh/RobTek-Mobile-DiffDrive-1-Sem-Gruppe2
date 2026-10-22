from machine import Pin
from rp2 import PIO, StateMachine, asm_pio
from time import sleep

@asm_pio(set_init=(PIO.OUT_LOW, PIO.OUT_LOW, PIO.OUT_LOW, PIO.OUT_LOW))
def PIO_set_step():
    wrap_target()

    mov(y, isr)             #
    label("step_0")         #
    mov(x, osr)             #1
    set(pins, 0b1100)         #1
    label("pwm_0")          #
    jmp(x_dec, "pwm_0")     #96
    set(pins, 0b0000) [30]    #31
    jmp(y_dec, "step_0")    #1

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
    def __init__(self, base_pin, sm_id=0, sm_freq=2_160_000, pwm_delay=96, step_repeats=138):
        self._sm = StateMachine(sm_id, PIO_set_step, freq=sm_freq, set_base=Pin(base_pin))
        
        self.update_delays(step_repeats, pwm_delay)

    
    def update_delays(self, new_step_repeats=None, new_pwm_delay=None):
        if new_step_repeats != None:
            self.step_repeats = new_step_repeats
        
        if new_pwm_delay != None:
            self.pwm_delay = new_pwm_delay
        
        self._sm.put(self.step_repeats)
        self._sm.exec("pull()")
        self._sm.exec("mov(isr, osr)")

        self._sm.put(self.pwm_delay)
        self._sm.exec("pull()")
    
    def stop(self):
        self._sm.active(0)
        self._sm.exec("set(pins, 0b00)")



try:
    PIO_stepper = StepperMotorPIO(base_pin=16, step_repeats=4000)
    PIO_stepper._sm.active(1)
    while True:
        pass

except:
    PIO_stepper.stop()