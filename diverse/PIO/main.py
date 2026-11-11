from time import sleep
from stepper_motor_PIO import StepperMotorPIO
import gc


PIO_stepper = StepperMotorPIO(sm_id=0, base_pin=0, pwm_freq=18_000)
PIO_stepper2 = StepperMotorPIO(sm_id=1, base_pin=4, pwm_freq=18_000)
try:
    """
    PIO_stepper._define_PWM_outputs()
    PIO_stepper2._define_PWM_outputs()
    PIO_stepper.set_step([1, 1, 0, 0], 0.2)
    PIO_stepper2.set_step([1, 1, 0, 0], 0.2)
    sleep(0.1)
    PIO_stepper.set_step([1, 1, 0, 0], 0.04)
    PIO_stepper2.set_step([1, 1, 0, 0], 0.04)
    sleep(0.2)
    
    PIO_stepper2.setup_PIO("forward", 0.002)
    PIO_stepper.setup_PIO("forward", 0.002)
    
    PIO_stepper.start_sm()
    PIO_stepper2.start_sm()
    sleep(5)
    
    """
    #for i in range(300, 30, -10):
    #    PIO_stepper.update_sm_pwm_delay(0.0001*i)
    #    PIO_stepper2.update_sm_pwm_delay(0.0001*i)
    #    sleep(0.1)
    
    #PIO_stepper.stop()
    #PIO_stepper._define_PWM_outputs()
    #PIO_stepper.set_step([1, 0, 0, 0], 0.5)
    
    PIO_stepper.start_move_sequences(200, 0.001, "half")
    PIO_stepper2.start_move_sequences(200, 0.001, "half")
    gc.collect()
    while PIO_stepper.currently_moving_stepper:
        PIO_stepper.move_stepper()
        PIO_stepper2.move_stepper(True)
        #sleep(0.0005)
    
    PIO_stepper2.stop()
    PIO_stepper.stop()
    #sleep(2)
    #PIO_stepper.stop()

except BaseException as e:
    print(e)
    PIO_stepper.stop()
    PIO_stepper2.stop()