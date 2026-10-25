from machine import Pin
from rp2 import PIO, StateMachine, asm_pio
from time import sleep

@asm_pio(set_init=(PIO.OUT_LOW, PIO.OUT_LOW, PIO.OUT_LOW, PIO.OUT_LOW))
def PIO_half_step():

    pwm_high = 0
    pwm_low = 31

    wrap_target()

    mov(y, osr)
    label("step_0")
    set(pins, 0b1100)   [pwm_high]
    set(pins, 0b0000)   [pwm_low]
    jmp(y_dec, "step_0")

    mov(y, osr)
    label("step_1")
    set(pins, 0b0100)   [pwm_high]
    set(pins, 0b0000)   [pwm_low]
    jmp(y_dec, "step_1")

    mov(y, osr)
    label("step_2")
    set(pins, 0b0110)   [pwm_high]
    set(pins, 0b0000)   [pwm_low]
    jmp(y_dec, "step_2")

    mov(y, osr)
    label("step_3")
    set(pins, 0b0010)   [pwm_high]
    set(pins, 0b0000)   [pwm_low]
    jmp(y_dec, "step_3")

    mov(y, osr)
    label("step_4")
    set(pins, 0b0011)   [pwm_high]
    set(pins, 0b0000)   [pwm_low]
    jmp(y_dec, "step_4")

    mov(y, osr)
    label("step_5")
    set(pins, 0b0001)   [pwm_high]
    set(pins, 0b0000)   [pwm_low]
    jmp(y_dec, "step_5")

    mov(y, osr)
    label("step_6")
    set(pins, 0b1001)   [pwm_high]
    set(pins, 0b0000)   [pwm_low]
    jmp(y_dec, "step_6")

    mov(y, osr)
    label("step_7")
    set(pins, 0b1000)   [pwm_high]
    set(pins, 0b0000)   [pwm_low]
    jmp(y_dec, "step_7")

    wrap()


class StepperMotorPIO:
    def __init__(self, base_pin, sm_id=0, sm_freq=2_160_000, pwm_repeats=138):
        self._sm = StateMachine(sm_id, PIO_half_step, freq=sm_freq, set_base=Pin(base_pin))
        self.pwm_repeats = step_rpwm_repeatsepeats
        self.update_delays(self.pwm_repeats)

    
    def update_delays(self, new_pwm_repeats):
        self.pwm_repeats = new_pwm_repeats
        self._sm.put(self.pwm_repeats)
        self._sm.exec("pull()")
    
    def stop(self):
        self._sm.active(0)
        self._sm.exec("set(pins, 0b0000)")


PIO_stepper = StepperMotorPIO(base_pin=19)
try:
    PIO_stepper._sm.active(1)
    while True:
        pass

except:
    PIO_stepper.stop()