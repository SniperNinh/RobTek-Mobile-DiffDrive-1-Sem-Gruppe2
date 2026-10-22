from stepper_motor import StepperMotor
from machine import Pin
from time import sleep
import math
for i in range(29):
    Pin(i, Pin.OUT).off()

class DifferentialDrive:
    def __init__(self, motor1:StepperMotor, motor2:StepperMotor, wheelbase, wheel_dia, steps_per_rev=200):
        self.motor1 = motor1
        self.motor2 = motor2
        self.wheelbase_circ = math.pi * wheelbase   
        self.wheel_circ = math.pi * wheel_dia
        self.steps_per_rev = steps_per_rev 
        self.phase1 = 0
        self.phase2 = 0        

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

        # iterate through all steps and set pwm of motors accordingly 
        for _ in range(total):

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

    def drive(self, distance: float, delay=0.002):
        """
        Rotates both motor the appropriate amount to move the robot a specific distance in mm

        Args:
            Distance (float): The physical distance to move the robot foward in mm\n
                if distance < 0 the robot drives backward
            Delay (float): The dalay to use when driving the motors
        """
        full_steps = abs(distance) / self.wheel_circ * self.steps_per_rev
        dir = "forward" if distance >= 0 else "backward"
        self._move(full_steps, delay, dir, dir)

    def turn_in_place(self, angle, delay=0.002):
        """
        Rotates the motors in opposing directions to make the robot rotate a given angle.

        Args:
            angle (float): the angle in degrees to rotate the robot in place
            delay (float): the delay to drive the motors with 
        """
        arc = self.wheelbase_circ * abs(angle) / 360

        full_steps = arc / self.wheel_circ * self.steps_per_rev

        if angle >= 0:
            self._move(full_steps, delay, "backward", "forward")
        else:
            self._move(full_steps, delay, "forward", "backward")

    def turn(self, angle, delay=0.002):
            """
            Rotates the motors in opposing directions to make the robot rotate a given angle.
    
            Args:
                angle (float): the angle in degrees to rotate the robot in place
                delay (float): the delay to drive the motors with 
            """
            arc = self.wheelbase_circ * abs(angle) / 360
    
            full_steps = arc / self.wheel_circ * self.steps_per_rev * 2
            
            if angle >= 0:
                self._move(full_steps, delay, "backward", "forward", False, True)
            else:
                self._move(full_steps, delay, "forward", "backward", True, False)
