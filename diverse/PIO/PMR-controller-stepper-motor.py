from machine import Pin, PWM
from rp2 import PIO, StateMachine, asm_pio
from time import sleep


"""
osr contains step sequence in progress
y contains current step
isr contains half step sequence
x contains reverse half step sequence

to reverse the sequence:
stop sm
move isr into osr
move x into isr
move osr into x


pull()
move osr into x
pull()
move osr into isr

wrap_target()

move step into y
jmp to loop if osr isnt empty

mov isr into osr

label loop
move y into pins
wait for irq
move 0 to pins
wait for irq
jmp to loop if pins is high

wait for pin to be high again
wrap()
"""

@asm_pio(set_init=(PIO.OUT_LOW, PIO.OUT_LOW, PIO.OUT_LOW, PIO.OUT_LOW))
def PIO_half_step():
    pull()
    mov(x, osr)
    pull()
    mov(isr, osr)

    wrap_target()

    out(y, 4)
    jmp(not_osre, "loop")
    mov(osr, isr)

    label("loop")
    mov(pins, y)
    wait(1, irq, 0)
    set(pins, 0)
    wait(0, irq, 0)
    jmp(pin, "loop")
    
    wait(1, pin, 0)
    wrap()

@asm_pio(set_init=(PIO.OUT_LOW))
def pio_irq_pwm():
    set(pins, 0b1)
    wrap_target()
    mov(x, osr)
    label("pwm_loop")
    set(pins, 0) [31]
    set(pins, 1) [7]
    jmp(x_dec, "pwm_loop")
    set(pins, 0b0)
    irq(clear, 0)
    nop() [31]
    set(pins, 0b1)
    wrap()


class StepperMotorPIO:
    def __init__(self, sm_id, sm_pwm_id, base_pin, delay_in, delay_out, delay=0.001, pwm_freq=22_000, pwm_pct=0.2):
        self._sm_direction = "forward"
        self._sm = StateMachine(sm_id, PIO_half_step, in_base=Pin(delay_in), set_base=Pin(base_pin))
        self._sm.put(0b1100_1000_1001_0001_0011_0010_0110_0100)
        self._sm.put(0b1100_0100_0110_0010_0011_0001_1001_1000)

        self._sm_pwm = StateMachine(sm_pwm_id, pio_irq_pwm, freq=20_000, set_base=Pin(delay_out))
        self._sm_pwm.put(22)
        self._sm_pwm.exec("pull()")


        #self.update_delay(delay)
    
    def start_sm(self):
        self._sm.active(1)
        self._sm_pwm.active(1)

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

        self._sm.put(int(abs(new_delay) * self.pwm_freq))
        self._sm.exec("pull()")
        self._sm.active(1)
        print(int(abs(new_delay * self.pwm_freq)), self._sm.active())
    
    def stop(self):
        self._sm.active(0)
        self._sm_pwm.active(0)
        self.sm_active = 0
        self._sm.exec("set(pins, 0b0000)")

stepper = StateMachine(1, pio_irq_pwm, freq=20_000, set_base=Pin(19))

stepper.active(1)

try:
    while True:
        pass
except BaseException as e:
    print(e)
    stepper.stop()
