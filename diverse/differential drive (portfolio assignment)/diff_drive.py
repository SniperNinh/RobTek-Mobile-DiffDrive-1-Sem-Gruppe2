from stepper_motor import StepperMotor
from PID import PID
from WiFiHandler import WifiHandler
from machine import Pin
from time import sleep, ticks_diff, ticks_us, sleep_us, ticks_add
import math
import gc
import _thread

class DifferentialDrive:
    def __init__(self, motor1:StepperMotor, motor2:StepperMotor, deviance:PID, controller:WifiHandler, wheelbase, wheel_dia, steps_per_rev=200, pid_period_us=100000, pid_scale=2000, min_delay=2000):
        self.motor1 = motor1
        self.motor2 = motor2
        self.wheelbase_circ = math.pi * wheelbase   
        self.wheel_circ = math.pi * wheel_dia
        self.steps_per_rev = steps_per_rev 
        self.phase1 = 0
        self.phase2 = 0
        self.deviance = deviance
        self.devianceDelay = 0        # shared value: written by core 1, read by core 0
        self.pid_running = False
        self.pid_period_us = pid_period_us   # how often the PID runs
        self.min_delay = min_delay  
        self.controller = controller
        self.controllerDataLoop_running = True

        self.motor1_accumulator = 0
        self.motor2_accumulator = 0

        self.out = 0

    def ramp_(self, start, end, total_accel_steps):
            v0sq = 1 / (start * start)
            v1sq = 1 / (end * end)
            return [int(1 / (v0sq + (v1sq - v0sq) * (i + 1) / total_accel_steps) ** 0.5)
                    for i in range(total_accel_steps)]

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
        # braking 25% of pwm
        seq1_brake = [[int(i * 0.25) for i in phase] for phase in seq1]
        seq2_brake = [[int(i * 0.25) for i in phase] for phase in seq2]

        steps_taken = 0
       
        next_step = ticks_us()

        initial_pwm = 0.2
 

        # iterate through all steps and set pwm of motors accordingly 
        for _ in range(total):
  
            
            

            # increment or decrement the phase index
            self.phase1 = (self.phase1 + c1) % n
            self.phase2 = (self.phase2 + c2) % n


            if driveMotor1:
                self.motor1.set_step(seq1[self.phase1])
            if driveMotor2:
                self.motor2.set_step(seq1[self.phase2])

            next_step = ticks_add(next_step, int(delay))

            remaining = ticks_diff(next_step, ticks_us())

            if remaining > 0:
                sleep_us(remaining)

            gc.collect()

            # increment o decrement total steps according to direction c1 and c2
            self.motor1.total_steps += c1
            self.motor2.total_steps += c2

        # set both motors phase to 25% of the last set phase to brake the motors
        self.motor1.set_step(seq1_brake[self.phase1])
        self.motor2.set_step(seq2_brake[self.phase2])


    def drive(self, distance: float, delay):
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

    def turn_in_place(self, angle, delay):
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



    def _PIDorControllerinnit(self, stepmode, microsteps=None):
            self.motor1.set_step_mode(stepmode, microsteps)
            self.motor2.set_step_mode(stepmode, microsteps)
            self.seq1 = self.motor1.modes[self.motor1.mode]
            self.seq2 = self.motor2.modes[self.motor2.mode]
            self.seqreverse = self.seq1.reverse()
            self.n = len(self.seq1)
            if len(self.seq2) != self.n:
                raise ValueError("both motors must use the same step mode")

        
            if self.controller.get_status():
                self.controllerDataLoop_running = True
                _thread.start_new_thread(self.controlDataLoop, ())
            else:
                self.pid_running = True
                _thread.start_new_thread(self._pid_loop, ())


    def _pid_loop(self):                     # runs on core 1
        try:
            while self.pid_running:
                self.dev = self.deviance.deviance()
                self.out = self.deviance.PID_update(self.dev)
                sleep_us(self.pid_period_us)
        except Exception as e:
            print("pid thread died:", e)  
            
    def _PID_Controller_stop(self):
        self.pid_running = False
        self.controllerDataLoop_running = False

    def ballsack(self, seq1, n):

        if self.motor1_accumulator >= 1.0:
            self.motor1_accumulator -= 1.0
            self.phase1 = (self.phase1 + 1) % n
        elif self.motor1_accumulator <= -1.0:
            self.motor1_accumulator += 1.0
            self.phase1 = (self.phase1 - 1) % n

        if self.motor2_accumulator >= 1.0:
            self.motor2_accumulator -= 1.0
            self.phase2 = (self.phase2 + 1) % n
        elif self.motor2_accumulator <= -1.0:
            self.motor2_accumulator += 1.0
            self.phase2 = (self.phase2 - 1) % n

        self.motor1.set_step(seq1[self.phase1])
        self.motor2.set_step(seq1[self.phase2])

    def runPID(self, max_pwm):

        self.motor1_accumulator += 1
        self.motor2_accumulator += 1

        turn_fraction = max(abs(self.out), 0)

        if self.out > 0: 
            self.motor2_accumulator -= turn_fraction
            self.motor2.v = max_pwm * min(1-turn_fraction, 1)
        else:
            self.motor1_accumulator -= turn_fraction
            self.motor1.v = max_pwm * min(1-turn_fraction, 1)


# KØR MÅSKE REVERSE HER!!
        self.ballsack(self.seq1, self.n)

    def controlDataLoop(self):
        try:
            while self.controllerDataLoop_running:
                self.y, self.z, self.button  = self.controller.get_data()
                sleep_us(self.pid_period_us)
        except Exception as e:
            print("controller thread died:", e) 


    def ballsackController(self, seq1, n, seqreverse):
        self.seqreverse = seqreverse
        if self.motor1_accumulator >= 100:
            self.motor1_accumulator -= 100.0
            self.phase1 = (self.phase1 + 1) % n

        if self.motor2_accumulator >= 100:
            self.motor2_accumulator -= 100.0
            self.phase2 = (self.phase2 + 1) % n
       
        self.motor1.set_step(seq1[self.phase1])
        self.motor2.set_step(seq1[self.phase2])
       


    def runcontroller(self, max_pwm):
        self.y, self.z, self.button  = self.controller.get_data()
        if -10 < self.z < 10:
            self.motor1_accumulator = 0
            self.motor2_accumulator = 0

        self.motor1_accumulator += min(abs(self.z), 100)
        self.motor2_accumulator += min(abs(self.z), 100)

        turn_fraction = max(abs(self.y), 0)

        if self.y > 0: 
            self.motor2_accumulator -= turn_fraction
            self.motor2.v = max_pwm * min(1-turn_fraction, 1)
        else:
            self.motor1_accumulator -= turn_fraction
            self.motor1.v = max_pwm * min(1-turn_fraction, 1)

          