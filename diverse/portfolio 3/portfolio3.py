from machine import ADC
from machine import Pin
from time import sleep, ticks_ms

led = Pin(10, Pin.OUT)

time_start = ticks_ms()

adcs = ADC(27)   # ADC0, ADC1, ADC2
led.toggle()

while False:
    data = adcs.read_u16()

    with open("log.txt", "a") as log:
        log.write(f"{(ticks_ms()-time_start)}; {data}\n")
        
    print(data)
    sleep(0.1)

