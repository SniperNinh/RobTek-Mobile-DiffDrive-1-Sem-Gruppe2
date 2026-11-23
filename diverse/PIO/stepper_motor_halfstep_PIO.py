from machine import Pin, PWM
from rp2 import PIO, StateMachine, asm_pio
from time import sleep

# Idea:
#  first pio program:
#   generates a pwm signal
#   



@asm_pio(sideset_init=(PIO.OUT_LOW))
def PIO_pwm():
    """
    high in ISR
    low in OSR
    (reasoning: if high reads from OSR, then when saving the low value in ISR, it's breifly in the OSR where high can read it)
    """
    wrap_target()

    mov(x, isr) .side(0b1)
    label("high_loop")
    jmp(x_dec, "high_loop")

    mov(x, osr) .side(0b0)
    label("low_loop")
    jmp(x_dec, "low_loop")
    
    wrap()


@asm_pio(set_init=(PIO.IN_HIGH), sideset_init=(PIO.OUT_LOW, PIO.OUT_LOW, PIO.OUT_LOW, PIO.OUT_LOW))
def PIO_half_step():
    """
    delay is saved as mount of times we repeat the same step
    delay is saved in the OSR
    """

    wrap_target()

    mov(y, osr)
    label("step_0")
    wait(0, pin, 0) .side(0b1100)
    wait(1, pin, 0) .side(0b0000)
    jmp(y_dec, "step_0")

    mov(y, osr)
    label("step_1")
    wait(0, pin, 0) .side(0b0100)
    wait(1, pin, 0) .side(0b0000)
    jmp(y_dec, "step_1")
    
    mov(y, osr)
    label("step_2")
    wait(0, pin, 0).side(0b0110)
    wait(1, pin, 0).side(0b0000)
    jmp(y_dec, "step_2")

    mov(y, osr)
    label("step_3")
    wait(0, pin, 0).side(0b0010)
    wait(1, pin, 0).side(0b0000)
    jmp(y_dec, "step_3")

    mov(y, osr)
    label("step_4")
    wait(0, pin, 0).side(0b0011)
    wait(1, pin, 0).side(0b0000)
    jmp(y_dec, "step_4")

    mov(y, osr)
    label("step_5")
    wait(0, pin, 0).side(0b0001)
    wait(1, pin, 0).side(0b0000)
    jmp(y_dec, "step_5")

    mov(y, osr)
    label("step_6")
    wait(0, pin, 0).side(0b1001)
    wait(1, pin, 0).side(0b0000)
    jmp(y_dec, "step_6")

    mov(y, osr)
    label("step_7")
    wait(0, pin, 0).side(0b1000)
    wait(1, pin, 0).side(0b0000)
    jmp(y_dec, "step_7")
    
    wrap()


class StepperMotorPIO:
    def __init__(self, motor_base, pwm_out, pwm_in, sm_motor_id=0, sm_pwm_id=4, sm_freq=5_120_000, pwm_repeats=40, pwm_cycles=256):
        self._sm_motor = StateMachine(sm_motor_id, PIO_half_step, freq=sm_freq, in_base=Pin(pwm_in), sideset_base=Pin(motor_base))
        self._sm_pwm   = StateMachine(sm_pwm_id, PIO_pwm, freq=sm_freq, sideset_base=Pin(pwm_out))
        self.pwm_cycles = pwm_cycles
        self.pwm_repeats = pwm_repeats
        self.update_pwm(0.2)
        self.update_delay(self.pwm_repeats)

    def update_pwm(self, new_pwm_pct):
        self.pwm_pct = new_pwm_pct
        high_cycles = int(self.pwm_cycles * new_pwm_pct -1)
        low_cycles = max(0, int(self.pwm_cycles - high_cycles -2))
        self._sm_pwm.put(high_cycles)
        self._sm_pwm.put(low_cycles)
        self._sm_pwm.exec("pull()")
        self._sm_pwm.exec("mov(isr, osr)")
        self._sm_pwm.exec("pull()")

    
    def update_delay(self, new_pwm_repeats):
        self.pwm_repeats = new_pwm_repeats
        self._sm_motor.put(self.pwm_repeats)
        self._sm_motor.exec("pull()")
    
    def stop(self):
        self._sm_pwm.active(0)
        self._sm_motor.active(0)
        self._sm_motor.exec("nop() .side(0b0000)")


PIO_stepper = StepperMotorPIO(motor_base=0, pwm_out=22, pwm_in=19)
pwm_pin = PWM(Pin(22))
pwm_pin.freq(22_000)
pwm_pin.duty_u16(int(0.2* (2**16)))
try:
    PIO_stepper._sm_motor.active(1)
    #PIO_stepper._sm_pwm.active(1)
    sleep(3)
    while True:
        pass

except:
    pwm_pin.duty_u16(0)
    PIO_stepper.stop()