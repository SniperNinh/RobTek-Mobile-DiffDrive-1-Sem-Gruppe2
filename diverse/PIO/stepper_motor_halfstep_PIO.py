from machine import Pin, PWM
from rp2 import PIO, StateMachine, asm_pio
from time import sleep




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
    def __init__(self, motor_base, pwm_in, sm_id=0, sm_pwm_id=4, sm_freq=840_000, pwm_repeats=37):
        self._sm_motor = StateMachine(sm_id, PIO_half_step, freq=sm_freq, in_base=Pin(pwm_in), sideset_base=Pin(motor_base))
        self.pwm_repeats = pwm_repeats
        self.update_delay(self.pwm_repeats)
    
    def update_delay(self, new_pwm_repeats):
        self.pwm_repeats = new_pwm_repeats
        self._sm_motor.put(self.pwm_repeats)
        self._sm_motor.exec("pull()")
    
    def stop(self):
        self._sm_motor.active(0)
        self._sm_motor.exec("nop() .side(0b0000)")


PIO_stepper = StepperMotorPIO(sm_id=0, motor_base=0, pwm_in=19)
PIO_stepper2 = StepperMotorPIO(sm_id=1, motor_base=4, pwm_in=18)

pwm_pin1 = PWM(Pin(22))
pwm_pin1.freq(24_000)
pwm_pin1.duty_u16(int(0.2* (2**16)))
pwm_pin2 = PWM(Pin(15))
pwm_pin2.freq(24_000)
pwm_pin2.duty_u16(int(0.2* (2**16)))
try:
    PIO_stepper._sm_motor.active(1)
    PIO_stepper2._sm_motor.active(1)
    sleep(3)
    while True:
        pass

except:
    pwm_pin1.duty_u16(0)
    pwm_pin2.duty_u16(0)
    PIO_stepper.stop()
    PIO_stepper2.stop()