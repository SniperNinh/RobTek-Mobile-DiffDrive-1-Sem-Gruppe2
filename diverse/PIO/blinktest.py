from machine import Pin
from rp2 import PIO, StateMachine, asm_pio
import time

@asm_pio(set_init=PIO.OUT_LOW)
def blink():
    pull(block)
    out(y, 32)
    wrap_target()
    mov(x, y)
    set(pins, 1)
    label("lp1")
    jmp(x_dec, "lp1")
    mov(x, y)
    set(pins, 0)
    label("lp2")
    jmp(x_dec, "lp2")
    wrap()

sm = StateMachine(0, blink, freq=2000, set_base=Pin(16))

sm.put(256)
sm.active(1)
time.sleep(3)
sm.active(0)