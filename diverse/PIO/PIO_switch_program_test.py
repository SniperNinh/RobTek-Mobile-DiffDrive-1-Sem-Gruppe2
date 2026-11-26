from rp2 import PIO, asm_pio, StateMachine
from machine import Pin
from time import sleep

"""
this is purely a test for wether or not you can change the program a statemachine is running on the fly
physical setup: 2 leds at GPIO 16 & 17, switch connected to GPIO 21
"""
"""
@asm_pio(set_init=(PIO.IN_HIGH), sideset_init=(PIO.OUT_LOW, PIO.OUT_LOW))
def alternating():
    wrap_target()
    wait(1, pin, 0) .side(0b10)
    wait(0, pin, 0)
    wait(1, pin, 0) .side(0b01)
    wait(0, pin, 0)
    wrap()
"""
@asm_pio(set_init=(PIO.IN_HIGH), sideset_init=(PIO.OUT_LOW, PIO.OUT_LOW))
def sync():
    wrap_target()
    label("high")
    nop() .side(0b11)
    jmp("high")
    label("low")
    nop() .side(0b00)
    jmp("low")
    wrap()

@asm_pio()
def empty():
    nop()
    nop()
    nop()
    nop()
    nop()
    nop()
    nop()
    nop()
    nop()
    nop()
    nop()
    nop()
    nop()
    nop()
    nop()
    nop()
    nop()
    nop()
    nop()
    nop()
    nop()
    nop()
    nop()
    nop()
    nop()
    nop()
    nop()
    nop()
    nop()
    nop()
    nop()
    nop()

pio = PIO(0)
pio.add_program(empty)
pio.remove_program()
sm = StateMachine(0, sync, in_base=21, sideset_base=16)

try:
    sm.active(1)
    sleep(1)
    for i in range(32):
        print("test: ", i)
        sm.exec(f"set(x, {i})")
        sm.exec("mov(pc, x)")
        sleep(1)
    """
    sm.active(0)
    pio.remove_program(alternating)
    pio.add_program(sync)
    sm.active(1)
    """
    while True:
        pass
except:
    sm.active(0)
    sm.exec("nop().side(0b00)")
