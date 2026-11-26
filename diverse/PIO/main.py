from stepper_motor_halfstep_PIO import StepperMotorPIO
from WiFiHandler import WifiHandler
from rp2 import PIO
from time import sleep

wifieee = WifiHandler("Redmi 9", "mr meowa", "10.230.172.167")

PIO(0).remove_program()
PIO(1).remove_program()

PIO_stepperleft = StepperMotorPIO(sm_id=0, base_pin=15, pwm_in=21, pwm_out=22)
PIO_stepperright = StepperMotorPIO(sm_id=5, base_pin=4, pwm_in=6, pwm_out=26)

try:
    PIO_stepperleft.start_sm()
    PIO_stepperright.start_sm()
    
    base_delay = 0.001

    while True:
        y_val, z_val, buttons = wifieee.get_data()
        y_val = random.randint(-100, 100)
        z_val = random.randint(-100, 100)

        if buttons & 0b01 == 0:
            PIO_stepperleft.stop()
            PIO_stepperright.stop()
            continue
        
        rotation = max(-100, min(100, y_val))/100
        # Deadzone
        if abs(rotation) < 0.2:
            rotation = 0
        
        speed = max(-100, min(100, z_val))/100
        # Deadzone
        if abs(speed) < 0.2:
            speed = 0
        
        if speed == 0 and rotation != 0:
            PIO_stepperright.update_delay(base_delay/rotation)
            PIO_stepperleft.update_delay(-base_delay/rotation)
        
        elif speed != 0:
            
            if rotation > 0:
                PIO_stepperright.update_delay(base_delay * (1 + rotation) /speed)
                PIO_stepperleft.update_delay(0.001/speed)
            else:
                PIO_stepperright.update_delay(0.001/speed)
                PIO_stepperleft.update_delay(base_delay * (1 - rotation) /speed)
        
        else:
            PIO_stepperleft.stop()
            PIO_stepperright.stop()

        sleep(0.1)

except BaseException as e:
    print(e)
    PIO_stepperleft.stop()
    PIO_stepperright.stop()
    wifieee.delete()
