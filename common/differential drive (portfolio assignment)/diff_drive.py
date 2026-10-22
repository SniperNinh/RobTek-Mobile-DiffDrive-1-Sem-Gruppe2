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

    def _move(self, full_steps, delay, dir1, dir2):
        #delay = max(delay, 0.001)
        seq1 = self.motor1.modes[self.motor1.mode]
        seq2 = self.motor2.modes[self.motor2.mode]
        n = len(seq1)
        if len(seq2) != n:
            raise ValueError("both motors must use the same step mode")

        total = round(full_steps * n / 4)
        c1 = 1 if dir1 == "forward" else -1
        c2 = 1 if dir2 == "forward" else -1
        stop_button = Pin(27, Pin.IN, Pin.PULL_UP)

        for _ in range(total):

            if stop_button.value() == False:
                break # stopper hvis knappen trykkes

            self.phase1 = (self.phase1 + c1) % n
            self.phase2 = (self.phase2 + c2) % n

            self.motor1.set_step(seq1[self.phase1])
            self.motor2.set_step(seq2[self.phase2])

            sleep(delay)

            self.motor1.total_steps += c1
            self.motor2.total_steps += c2

        # set both motors phase to 25% of the last set phase to brake the motors
        self.motor1.set_step([i*0.25 for i in seq1[self.phase1]])
        self.motor2.set_step([i*0.25 for i in seq2[self.phase2]])

    def drive(self, distance, delay=0.002):
        full_steps = abs(distance) / self.wheel_circ * self.steps_per_rev
        dir = "forward" if distance >= 0 else "backward"
        self._move(full_steps, delay, dir, dir)

    def turn_in_place(self, angle, delay=0.002):
        arc = self.wheelbase_circ * abs(angle) / 360
        full_steps = arc / self.wheel_circ * self.steps_per_rev
        if angle >= 0:
            self._move(full_steps, delay, "backward", "forward")
        else:
            self._move(full_steps, delay, "forward", "backward")

"""Tuning"""
pwm = 0.75
stepmode = "half"
Microsteps = None
Delay = 0.001


motor1 = StepperMotor([0, 3, 1, 2], pwm_pct=pwm, frequency=18_000)
motor2 = StepperMotor([4, 5, 6, 7], pwm_pct=pwm, frequency=18_000)
motor1.set_step_mode(stepmode, microsteps=Microsteps)
motor2.set_step_mode(stepmode, microsteps=Microsteps)

robot = DifferentialDrive(motor1, motor2, wheelbase=233, wheel_dia=87, steps_per_rev=200)

sleep(5) # wait 5 seconds to give us time to get the robot in place

# drive around a square meter
for i in range(4):
    robot.drive((1000), delay=Delay)
    sleep(0.5)
    robot.turn_in_place(90, delay=Delay)
    sleep(0.5)

robot.motor1.stop()
robot.motor2.stop()
