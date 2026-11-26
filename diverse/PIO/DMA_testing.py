from rp2 import DMA, PIO, StateMachine, asm_pio
from time import sleep
from machine import Pin


@asm_pio(set_init=(PIO.IN_HIGH), sideset_init=(PIO.OUT_LOW, PIO.OUT_LOW))
def alternating():
    wrap_target()
    wait(1, pin, 0) .side(0b10)
    wait(0, pin, 0)
    wait(1, pin, 0) .side(0b01)
    wait(0, pin, 0)
    wait(1, pin, 0) .side(0b10)
    wait(0, pin, 0)
    wait(1, pin, 0) .side(0b01)
    wait(0, pin, 0)
    wait(1, pin, 0) .side(0b10)
    wait(0, pin, 0)
    wait(1, pin, 0) .side(0b01)
    wait(0, pin, 0)
    wait(1, pin, 0) .side(0b10)
    wait(0, pin, 0)
    wait(1, pin, 0) .side(0b01)
    wait(0, pin, 0)
    wait(1, pin, 0) .side(0b10)
    wait(0, pin, 0)
    wait(1, pin, 0) .side(0b01)
    wait(0, pin, 0)
    wait(1, pin, 0) .side(0b10)
    wait(0, pin, 0)
    wait(1, pin, 0) .side(0b01)
    wait(0, pin, 0)
    wait(1, pin, 0) .side(0b10)
    wait(0, pin, 0)
    wait(1, pin, 0) .side(0b01)
    wait(0, pin, 0)
    wait(1, pin, 0) .side(0b10)
    wait(0, pin, 0)
    wait(1, pin, 0) .side(0b01)
    wait(0, pin, 0)
    wrap()


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


sm = StateMachine(0, sync, in_base=21, sideset_base=16)
sm.active(1)
dma = DMA()

def read_addr(addr):
    output = bytearray(1)
    d = rp2.DMA()
    c = d.pack_ctrl(
        size=2,
        inc_read=False
    )

    # The count is in 'transfers', which defaults to four-byte words, so divide length by 4
    d.config(
        read=addr,
        write=output,
        count=1,
        ctrl=c,
        trigger=True
    )
    # Wait for completion
    while d.active():
        pass
    d.close()
    return output

pin = Pin(20, Pin.OUT)


print(read_addr(0x502000d4)[0])
sleep(1)
sm.exec("set(x, 2)")
sm.exec("mov(pc, x)")
print(read_addr(0x502000d4)[0])

