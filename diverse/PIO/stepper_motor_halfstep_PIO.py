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


@asm_pio(set_init=(PIO.IN_HIGH), sideset_init=(PIO.OUT_LOW, PIO.OUT_LOW, PIO.OUT_LOW, PIO.OUT_LOW))
def PIO_reverse_half_step():
    """
    PIO assembly code for stepping through a half-step sequence.
    It synchronises with the 'in_base' input pin,
    where it follows the high-low timing.
    (as in, its step goes high when input is high, and output low when input is low)

    It repeats a step the amount of times stored in the OSR
    """

    wrap_target()

    mov(y, osr)
    label("step_7")
    wait(0, pin, 0).side(0b1000)
    wait(1, pin, 0).side(0b0000)
    jmp(y_dec, "step_7")

    mov(y, osr)
    label("step_6")
    wait(0, pin, 0).side(0b1001)
    wait(1, pin, 0).side(0b0000)
    jmp(y_dec, "step_6")

    mov(y, osr)
    label("step_5")
    wait(0, pin, 0).side(0b0001)
    wait(1, pin, 0).side(0b0000)
    jmp(y_dec, "step_5")

    mov(y, osr)
    label("step_4")
    wait(0, pin, 0).side(0b0011)
    wait(1, pin, 0).side(0b0000)
    jmp(y_dec, "step_4")

    mov(y, osr)
    label("step_3")
    wait(0, pin, 0).side(0b0010)
    wait(1, pin, 0).side(0b0000)
    jmp(y_dec, "step_3")
    
    mov(y, osr)
    label("step_2")
    wait(0, pin, 0).side(0b0110)
    wait(1, pin, 0).side(0b0000)
    jmp(y_dec, "step_2")

    mov(y, osr)
    label("step_1")
    wait(0, pin, 0) .side(0b0100)
    wait(1, pin, 0) .side(0b0000)
    jmp(y_dec, "step_1")

    mov(y, osr)
    label("step_0")
    wait(0, pin, 0) .side(0b1100)
    wait(1, pin, 0) .side(0b0000)
    jmp(y_dec, "step_0")
    
    wrap()


class StepperMotorPIO:
    def __init__(self, sm_id, base_pin, pwm_in, pwm_out, delay=0.001, pwm_freq=22_000, pwm_pct=0.2):
        """
        sm_id    ; the id of the statemachine to use, 0-3 & 4-7 are avaliable
        base_pin ; is the first GPIO pin for the output to the steppermotor, will define the base_pin + the next 3 pins
        pwm_in   ; the GPIO pin the statemachine follows for timing the step sequence
        pwm_out  ; the GPIO pin the stepper motor object defines as output for its pwm
        (pwm_in and pwm_out needs to be connected with a wire in hardware)
        delay    ; the default delay defined in the beginning
        pwm_freq ; the targeted frequency of the pwm
        pwm_pct  ; the default pwm duty cycle defined in the beginning
        """
        self.pio = PIO(sm_id % 4)
        self._sm_direction = "forward"
        self._sm = StateMachine(sm_id, PIO_half_step, in_base=Pin(pwm_in), sideset_base=Pin(base_pin))

        self.pwm = PWM(Pin(pwm_out))
        self.pwm_freq = pwm_freq
        self.pwm.freq(pwm_freq)
        self.pwm.duty_u16(int(pwm_pct * (2**16 - 1)))
        self.update_delay(delay)
    
    def start_sm(self):
        self._sm.active(1)

    def update_delay(self, new_delay):
        """
        Math for calculating precise delays
        floor(target_pwm_freq * new_delay) = step_repeats
        step_repeats/new_delay = actual_pwm_freq
        """
        #print(new_delay, int(new_delay * self.pwm_freq))
        if new_delay >= 0:
            new_direction = "forward"
        else:
            new_direction = "backward"

        self._sm.active(0)
        if self._sm_direction != new_direction:
            self._sm_direction = new_direction
            self.pio.remove_program()
            if self._sm_direction == "forward":
                self.pio.add_program(PIO_half_step)
            else:
                self.pio.add_program(PIO_half_step)

        print(int(abs(new_delay * self.pwm_freq)))
        self._sm.put(int(abs(new_delay) * self.pwm_freq))
        self._sm.exec("pull()")
        self._sm.active(1)
    
    def stop(self):
        self._sm.active(0)
        self.sm_active = 0
        self._sm.exec("nop() .side(0b0000)")

