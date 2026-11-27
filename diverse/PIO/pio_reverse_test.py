from rp2 import PIO, StateMachine, asm_pio
from machine import Pin
from time import sleep

"""
this file im testing the mov(x, reverse(y)) functionality of the PIO
"""


@asm_pio()
def pio_reverse_program():
    wrap_target()
    pull()
    mov(isr, osr)
    push()
    mov(isr, osr)
    mov(isr, reverse(isr))
    push()
    wrap()


sm = StateMachine(0, pio_reverse_program)

sm.active(1)

sm.put(0b11000100011000100011000110011000)
print(bin(sm.get()))
print(bin(sm.get()))
