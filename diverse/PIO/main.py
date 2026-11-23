from time import sleep
from stepper_motor_PIO import StepperMotorPIO
from diff_drive_pio import DifferentialDrive
import gc



PIO_stepper = StepperMotorPIO(sm_id=0, base_pin=0, pwm_freq=18_000)
PIO_stepper2 = StepperMotorPIO(sm_id=1, base_pin=4, pwm_freq=18_000)
"""
robot = DifferentialDrive(wheelbase=240, wheel_dia=87, steps_per_rev=50)

"""
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


    PIO_stepper.setup_PIO(0.0028, 0.2)
    PIO_stepper2.setup_PIO(0.004, 0.2)
    
    PIO_stepper.start_sm()
    PIO_stepper2.start_sm()
    sleep(1)
    #PIO_stepper.update_sm_pwm_delay(0.002)
    #PIO_stepper2.update_sm_pwm_delay(0.002)
    sleep(3)
    PIO_stepper.stop()
    PIO_stepper2.stop()
    """
    PIO_stepper._define_PWM_outputs()
    PIO_stepper2._define_PWM_outputs()

    PIO_stepper.start_move_sequences(200, 0.002, "half", direction="backward")
    PIO_stepper2.start_move_sequences(200, 0.0014, "half", direction="backward")

    print(PIO_stepper.delay)
    print(PIO_stepper2.delay)

    while PIO_stepper.currently_moving_stepper:
        PIO_stepper.move_stepper()
        PIO_stepper2.move_stepper(True)
    
    PIO_stepper.stop()
    PIO_stepper2.stop()

    """
    gc.collect()
    robot.drive_straight(2000, step_mode="full", delay=0.0025)
    robot.turn_in_place(-92, step_mode="full", delay=0.0025)
    robot.drive_straight(2000, step_mode="full", delay=0.0025)
    robot.turn_in_place(-92, step_mode="full", delay=0.0025)
    robot.drive_straight(3800, step_mode="full", delay=0.0025)
    robot.turn_in_place(-92, step_mode="full", delay=0.0025)
    robot.drive_straight(2000, step_mode="full", delay=0.0025)
    robot.turn_in_place(-91, step_mode="full", delay=0.0025)
    robot.drive_straight(1800, step_mode="full", delay=0.0025)

    robot.run_continuously()
    for i in range (-30, 30):
        robot.update_continuous_ratio(i*0.1)
        sleep(0.5)

    robot.stop()
    """
    #sleep(2)
    #PIO_stepper.stop()

except BaseException as e:
    print(e)
    """
    robot.stop()
    
    """
    PIO_stepper.stop()
    PIO_stepper2.stop()