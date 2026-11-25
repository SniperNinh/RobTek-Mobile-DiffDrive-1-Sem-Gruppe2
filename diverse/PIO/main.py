from stepper_motor_halfstep_PIO import StepperMotorPIO
from WiFiHandler import WifiHandler

wifieee = WifiHandler("Redmi 9", "mr meowa", "10.230.172.167")

PIO_stepperleft = StepperMotorPIO(sm_id=0, base_pin=0, pwm_in=19, pwm_out=22)
PIO_stepperright = StepperMotorPIO(sm_id=1, base_pin=4, pwm_in=18, pwm_out=26)

try:
    
    PIO_stepperleft._sm_motor.active(1)
    PIO_stepperright._sm_motor.active(1)
    
    
    while True:
        """
        print(wifieee.get_data())
        continue
        """
        y_val, z_val, buttons = wifieee.get_data()
        print(y_val)
        rotation = max(-100, min(100, y_val))/100
        #print(rotation)
        if rotation > 0:
            PIO_stepperright.update_delay(rotation*0.001+0.001)
            PIO_stepperleft.update_delay(0.001)
            #print("high")
        else:
            PIO_stepperright.update_delay(0.001)
            PIO_stepperleft.update_delay(-rotation*0.001+0.001)
            #print("low")
except:
    
    PIO_stepperleft.stop()
    PIO_stepperright.stop()

PIO_stepperleft.stop()
PIO_stepperright.stop()