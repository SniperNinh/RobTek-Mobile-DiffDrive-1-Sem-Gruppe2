from machine import ADC
from machine import Pin
from time import sleep, ticks_ms

from stepper_motor import StepperMotor

from diff_drive import DifferentialDrive


class DiffDriveWithLogger(DifferentialDrive):
    def __init__(self, motor1: StepperMotor, motor2: StepperMotor, wheelbase, wheel_dia, steps_per_rev=200):
        super().__init__(motor1, motor2, wheelbase, wheel_dia, steps_per_rev)

        self.led = Pin(10, Pin.OUT)
        self.time_start = ticks_ms()
        self.adcs = ADC(27)
        self.led.toggle()

    def _move(self, full_steps: int, delay: float, dir1, dir2, driveMotor1 = True, driveMotor2 = True):
            """
            Rotates both motors a given number of full steps with a given delay. 
            Each motor direction is controlled independently with dir1 and dir2.
            
            Args:
                full_steps (int): the number of full steps to rotate both motors
                delay (float): the time in seconds to pause between updating the phase of the motors
                dir1 (str): the direction "foward" or "backward" to rotate the first motor
                dir2 (str): the direction "foward" or "backward" to rotate the second motor
            """
    
            # set the stepping mode for both motors and make sure that they are the same
            seq1 = self.motor1.modes[self.motor1.mode]
            seq2 = self.motor2.modes[self.motor2.mode]
            n = len(seq1)
            if len(seq2) != n:
                raise ValueError("both motors must use the same step mode")
    
            # set the total number of sequence executions and motor directions
            total = round(full_steps * n / 4)
            c1 = 1 if dir1 == "forward" else -1
            c2 = 1 if dir2 == "forward" else -1
    
            # init button to stop the motors in action
            stop_button = Pin(27, Pin.IN, Pin.PULL_UP)

            steps_taken = 0
    
            # iterate through all steps and set pwm of motors accordingly 
            for _ in range(total):

                steps_taken += 1

                with open("log.txt", "a") as log:
                    data = self.adcs.read_u16()
                    log.write(f"{ticks_ms()-self.time_start}; {(180/full_steps)*steps_taken}; {data} \n")
    
                if stop_button.value() == False:
                    break # stopper hvis knappen trykkes
    
                # increment or decrement the phase index
                self.phase1 = (self.phase1 + c1) % n
                self.phase2 = (self.phase2 + c2) % n
    
                # apply pwm to motors
                self.motor1.set_step(seq1[self.phase1])
                self.motor2.set_step(seq2[self.phase2])
    
                sleep(delay)
    
                # increment o decrement total steps according to direction c1 and c2
                self.motor1.total_steps += c1
                self.motor2.total_steps += c2
    
            # set both motors phase to 25% of the last set phase to brake the motors
            if driveMotor1:
                self.motor1.set_step([i*0.25 for i in seq1[self.phase1]])
            if driveMotor2:
                self.motor2.set_step([i*0.25 for i in seq2[self.phase2]])


"""Tuning"""
pwm = 0.75
stepmode = "half"
Microsteps = None
Delay = 0.001

# init motors and modes
motor1 = StepperMotor([0, 3, 1, 2], pwm_pct=pwm, frequency=18_000) # pins are ordered weird on this motor because the wires are twisted
motor2 = StepperMotor([4, 5, 6, 7], pwm_pct=pwm, frequency=18_000)
motor1.set_step_mode(stepmode, microsteps=Microsteps)
motor2.set_step_mode(stepmode, microsteps=Microsteps)

# init differential drive object
robot = DiffDriveWithLogger(motor1, motor2, wheelbase=233, wheel_dia=87, steps_per_rev=200)

sleep(5)

robot.turn_in_place(-180, Delay)