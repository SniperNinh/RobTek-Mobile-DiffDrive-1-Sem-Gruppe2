from machine import Pin, PWM
from rp2 import PIO, StateMachine, asm_pio
from time import sleep


@asm_pio(set_init=(PIO.IN_HIGH), sideset_init=(PIO.OUT_LOW, PIO.OUT_LOW, PIO.OUT_LOW, PIO.OUT_LOW))
def PIO_half_step():
    """
    PIO assembly code for stepping through a half-step sequence.
    It synchronises with the 'in_base' input pin,
    where it follows the high-low timing.
    (as in, its step goes high when input is high, and output low when input is low)

    It repeats a step the amount of times stored in the OSR
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
    def __init__(self, sm_id, base_pin, pwm_in, pwm_out, delay=0.001, pwm_freq=22_000, pwm_pct=0.2):
        """
        base_pin ; is the first GPIO pin for the output to the steppermotor, will define the base_pin + the next 3 pins
        pwm_in   ; the GPIO pin the statemachine follows for timing the step sequence
        pwm_out  ; the GPIO pin the stepper motor object defines as output for its pwm
        (pwm_in and pwm_out needs to be connected through hardware)
        sm_id    ; the id of the statemachine to use, 0-3 & 4-7 are avaliable
        delay    ; the default delay defined in the beginning
        pwm_freq ; the targeted frequency of the pwm
        pwm_pct  ; the default pwm duty cycle defined in the beginning
        """
        self.pwm_freq = pwm_freq
        self._sm_motor = StateMachine(sm_id, PIO_half_step, in_base=Pin(pwm_in), sideset_base=Pin(base_pin))
        self.pwm = PWM(Pin(pwm_out))
        self.pwm.freq(pwm_freq)
        self.pwm.duty_u16(int(pwm_pct * (2**16 - 1)))
        self.update_delay(delay)
    
    def update_delay(self, new_delay):
        """
        Math for calculating precise delays
        floor(target_pwm_freq * new_delay) = step_repeats
        step_repeats/new_delay = actual_pwm_freq
        """
        #print(new_delay, int(new_delay * self.pwm_freq))
        self._sm_motor.put(int(new_delay * self.pwm_freq))
        self._sm_motor.exec("pull()")
    
    def stop(self):
        self._sm_motor.active(0)
        self._sm_motor.exec("nop() .side(0b0000)")



from WiFiHandler import WifiHandler

wifieee = WifiHandler("Redmi 9", "mr meowa", "10.230.172.167")

PIO_stepperleft = StepperMotorPIO(sm_id=0, base_pin=0, pwm_in=19, pwm_out=22)
PIO_stepperright = StepperMotorPIO(sm_id=1, base_pin=4, pwm_in=18, pwm_out=26)

try:
    
    PIO_stepperleft._sm_motor.active(1)
    PIO_stepperright._sm_motor.active(1)
    
    
    while True:
        """
        print(wifieee.get_data())
        continue
        """
        y_val, z_val, buttons = wifieee.get_data()
        print(y_val)
        rotation = max(-100, min(100, y_val))/100
        #print(rotation)
        if rotation > 0:
            PIO_stepperright.update_delay(rotation*0.001+0.001)
            PIO_stepperleft.update_delay(0.001)
            #print("high")
        else:
            PIO_stepperright.update_delay(0.001)
            PIO_stepperleft.update_delay(-rotation*0.001+0.001)
            #print("low")
except:
    
    PIO_stepperleft.stop()
    PIO_stepperright.stop()

PIO_stepperleft.stop()
PIO_stepperright.stop()