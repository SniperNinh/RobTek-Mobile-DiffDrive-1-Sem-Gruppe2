from stepper_motor_PIO import StepperMotorPIO
from machine import Pin
from time import sleep
import math

class DifferentialDrive:
    def __init__(self, wheelbase, wheel_dia, steps_per_rev=50):
        self.motorLeft = StepperMotorPIO(sm_id=0, base_pin=0)
        self.motorRight = StepperMotorPIO(sm_id=1, base_pin=4)
        self.wheelbase_circ = math.pi * wheelbase
        self.wheel_circ = math.pi * wheel_dia
        self.steps_per_rev = steps_per_rev

    def _move(self, sequences, delayLeft, delayRight, dirLeft, dirRight, step_mode, microsteps=None, lock_motor=False):
        print(dirLeft, dirRight)
        self.motorLeft.start_move_sequences(sequences=sequences, delay=delayLeft, step_mode=step_mode, microsteps=microsteps, direction=dirLeft)
        self.motorRight.start_move_sequences(sequences=sequences, delay=delayRight, step_mode=step_mode, microsteps=microsteps, direction=dirRight)
        while self.motorLeft.currently_moving_stepper or self.motorRight.currently_moving_stepper:
            if self.motorLeft.move_stepper():
                if lock_motor: self.motorLeft.lock_motor(self.motorLeft.current_sequence[self.motorLeft.current_step])
                else: self.motorLeft.stop()
            if self.motorRight.move_stepper(True):
                if lock_motor: self.motorRight.lock_motor(self.motorRight.current_sequence[self.motorRight.current_step])
                else: self.motorRight.stop()

    def drive_straight(self, distance, step_mode="full", lock_motor=False, delay=0.002):
        sequences = int(abs(distance) / self.wheel_circ * self.steps_per_rev)
        dir = "forward" if distance >= 0 else "backward"
        self._move(
            sequences=sequences,
            delayLeft=delay,
            delayRight=delay,
            dirLeft=dir,
            dirRight=dir,
            step_mode=step_mode,
            lock_motor=lock_motor
            )

    def turn_in_place(self, angle, step_mode="full", lock_motor=False, delay=0.002):
        arc = self.wheelbase_circ * abs(angle) / 360
        sequences = int(arc / self.wheel_circ * self.steps_per_rev)
        if angle >= 0:
            dirLeft="backward"
            dirRight="forward"
        else:
            dirLeft="forward"
            dirRight="backward"
        self._move(
            sequences=sequences,
            delayLeft=delay,
            delayRight=delay,
            dirLeft=dirLeft,
            dirRight=dirRight,
            step_mode=step_mode,
            lock_motor=lock_motor
            )
    
    def stop(self):
        self.motorLeft.stop()
        self.motorRight.stop()
