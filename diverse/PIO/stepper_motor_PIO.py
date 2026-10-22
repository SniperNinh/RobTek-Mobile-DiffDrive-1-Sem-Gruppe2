from machine import Pin
from rp2 import PIO, StateMachine, asm_pio
from time import sleep

@asm_pio(set_init=(PIO.OUT_LOW, PIO.OUT_LOW, PIO.OUT_LOW, PIO.OUT_LOW))
def PIO_set_step():
    wrap_target()
    






sm = StateMachine(0, blink_delay, freq=3000, set_base=Pin(15))

sm.put(256)
sm.exec("pull(block)")

sm.active(1)
sleep(3)
sm.put(128)
sm.exec("pull(block)")
sleep(3)
sm.active(0)

