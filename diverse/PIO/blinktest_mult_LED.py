# this python files is for testing changing a delay in the statemachine while its running
from machine import Pin
from rp2 import PIO, StateMachine, asm_pio
from time import sleep

@asm_pio(set_init=(PIO.OUT_LOW, PIO.OUT_LOW))
def blink_delay():
    wrap_target()
    mov(x, osr)
    set(pins, 2)
    label("lp1")
    jmp(x_dec, "lp1")
    mov(x, osr)
    set(pins, 0)
    label("lp2")
    jmp(x_dec, "lp2")
    wrap()

sm = StateMachine(0, blink_delay, freq=3000, set_base=Pin(15))

sm.put(256)
sm.exec("pull(block)")

sm.active(1)
sleep(3)
sm.put(128)
sm.exec("pull(block)")
sleep(3)
sm.active(0)

