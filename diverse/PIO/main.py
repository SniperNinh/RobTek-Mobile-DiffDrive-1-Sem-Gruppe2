from stepper_motor_halfstep_PIO import StepperMotorPIO
from WiFiHandler import WifiHandler
from rp2 import PIO
from time import sleep
from machine import Pin

Pin("LED").off()

wifieee = WifiHandler("Redmi 9", "mr meowa", "10.230.172.167")

Pin("LED").on()

PIO_stepperleft = StepperMotorPIO(sm_id=0, base_pin=0, pwm_in=16, pwm_out=17)
PIO_stepperright = StepperMotorPIO(sm_id=1, base_pin=4, pwm_in=18, pwm_out=19)

try:
    #PIO_stepperleft.start_sm()
    #PIO_stepperright.start_sm()
    
    base_delay = 0.0008

    #import random

    while True:
        y_val, z_val, buttons = wifieee.get_data()
        #y_val = random.randint(-100, 100)
        #z_val = random.randint(-100, 100)
        if buttons & 0b10 != 0:
            raise BaseException("emergency stop")

        if buttons & 0b01 == 0:
            PIO_stepperleft.stop()
            PIO_stepperright.stop()
            continue
        
        rotation = max(-100, min(100, y_val))/100
        # Deadzone
        if abs(rotation) < 0.2:
            rotation = 0
        
        speed = max(0, min(100, z_val))/100
        # Deadzone
        if abs(speed) < 0.3:
            speed = 0
        
        
        if speed != 0:
            PIO_stepperleft.start_sm()
            PIO_stepperright.start_sm()
            if rotation > 0:
                PIO_stepperright.update_delay(base_delay * (1 + rotation) /speed)
                PIO_stepperleft.update_delay(base_delay/speed)
            elif rotation < 0:
                PIO_stepperright.update_delay(base_delay/speed)
                PIO_stepperleft.update_delay(base_delay * (1 - rotation) /speed)
            else:
                PIO_stepperleft.update_delay(base_delay/speed)
                PIO_stepperright.update_delay(base_delay/speed)

        else:
            PIO_stepperleft.stop()
            PIO_stepperright.stop()

        sleep(0.01)

except BaseException as e:
    print(e)
    PIO_stepperleft.stop()
    PIO_stepperright.stop()
    wifieee.delete()
    Pin("LED").off()
