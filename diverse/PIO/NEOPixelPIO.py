# Example using PIO to drive a set of WS2812 LEDs.
from time import sleep, sleep_ms
from machine import Pin
import rp2, array, math

# Configure the number of WS2812 LEDs.
NUM_LEDS = 2


@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def ws2812():
    T1 = 2
    T2 = 5
    T3 = 3
    wrap_target()
    label("bitloop")
    out(x, 1)               .side(0)    [T3 - 1]
    jmp(not_x, "do_zero")   .side(1)    [T1 - 1]
    jmp("bitloop")          .side(1)    [T2 - 1]
    label("do_zero")
    nop()                   .side(0)    [T2 - 1]
    wrap()


# Create the StateMachine with the ws2812 program, outputting on Pin(22).
sm = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=Pin(22))



colors2 = [int((2**6) * math.sin(i*math.pi/14)) for i in range(9)]
colors = [
    0b001111110000000000000000,
    0b001110100001100000000000,
    0b001011010010110100000000,
    0b000110000011101000000000,
    0b000000000011111100000000,
    0b000000000011101000011000,
    0b000000000010110100101101,
    0b000000000001100000111010,
    0b000000000000000000111111,
    0b000110000000000000111010,
    0b001011010000000000101101,
    0b001110100000000000011000
    ]

def get_rgb(magnitude, angle):
    r = max(0, int(magnitude * math.cos(angle*math.pi/180)))
    g = max(0, int(magnitude * math.sin(angle*math.pi/180)))
    b = max(0, int(magnitude * (-math.cos(angle*math.pi/180))))
    return g * (2**16) + r * (2**8) + b

color_array = array.array("I", [0, 0])

# Start the StateMachine, it will wait for data on its FIFO.
sm.active(1)
i = 0
#sm.put(255*(2**16) + 192 * (2**8) + 203)


try:
    while True:
        color_array[0] = get_rgb(2**6, i)
        print(i, ":", hex(get_rgb(2**6, i)))
        color_array[1] = get_rgb(2**6, i+180)
        sm.put(color_array, 8)
        i += 1
        sleep_ms(50)
except:
    sm.put(array.array("I", [0, 0]))
