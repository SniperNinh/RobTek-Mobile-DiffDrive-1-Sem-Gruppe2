from machine import ADC
from machine import Pin
from time import sleep, ticks_ms

from stepper_motor import StepperMotor

from diff_drive import DifferentialDrive


class DiffDriveWithLogger(DifferentialDrive):
    def __init__(self, motor1: StepperMotor, motor2: StepperMotor, wheelbase, wheel_dia, steps_per_rev=200):
        super().__init__(motor1, motor2, wheelbase, wheel_dia, steps_per_rev)

        self.led = Pin(10, Pin.OUT)
        self.adcs = ADC(27)
        self.led.toggle()
        self.time_start = ticks_ms()

        self.log_cooldown = 1000/50 # 10 logs per second
        self.last_log_time = ticks_ms()

        self.log_data = ""

    def _move(self, full_steps, delay, dir1, dir2, driveMotor1=True, driveMotor2=True):
        seq1 = self.motor1.modes[self.motor1.mode]
        seq2 = self.motor2.modes[self.motor2.mode]
        n = len(seq1)
        if len(seq2) != n:
            raise ValueError("both motors must use the same step mode")

        total = round(full_steps * n / 4)
        c1 = 1 if dir1 == "forward" else -1
        c2 = 1 if dir2 == "forward" else -1
        
        try:
            for _ in range(total):
                self.motor1.total_steps += c1
                self.motor2.total_steps += c2

                if self.last_log_time + self.log_cooldown < ticks_ms():
                    self.last_log_time = ticks_ms()
                    # Signed heading in degrees; positive is the direction of turn_in_place(+).
                    wheel_steps = (self.motor2.total_steps - self.motor1.total_steps) / 2
                    robot_deg = wheel_steps * 4 / n / self.steps_per_rev * 360 \
                                * self.wheel_circ / self.wheelbase_circ

                    t = ticks_ms() - self.time_start
                    adc = self.adcs.read_u16()
                    self.log_data += f"{t}, {robot_deg}, {adc}\n"


                self.phase1 = (self.phase1 + c1) % n
                self.phase2 = (self.phase2 + c2) % n
                if driveMotor1:
                    self.motor1.set_step(seq1[self.phase1])
                if driveMotor2:
                    self.motor2.set_step(seq2[self.phase2])
                sleep(delay)
        finally:
            # hold at 25% so the robot doesn't drift between legs
            self.motor1.set_step([i * 0.25 for i in seq1[self.phase1]])
            self.motor2.set_step([i * 0.25 for i in seq2[self.phase2]])


"""Tuning"""
pwm = 0.2
stepmode = "half"
Microsteps = None
Delay = 0.005

# init motors and modes
motor1 = StepperMotor([0, 3, 1, 2], pwm_pct=pwm, frequency=18_000) # pins are ordered weird on this motor because the wires are twisted
motor2 = StepperMotor([4, 5, 6, 7], pwm_pct=pwm, frequency=18_000)
motor1.set_step_mode(stepmode, microsteps=Microsteps)
motor2.set_step_mode(stepmode, microsteps=Microsteps)

# init differential drive object
robot = DiffDriveWithLogger(motor1, motor2, wheelbase=238, wheel_dia=87, steps_per_rev=200)

sleep(1)


sleep(1)

try:
    print("start")

    robot.turn_in_place(180, Delay)
    sleep(2)

    robot.turn_in_place(-180, Delay)

    with open("log.csv", "a") as log:
        log.write(robot.log_data)

    print("done", motor1.total_steps, motor2.total_steps)

finally:
    motor1.stop()
    motor2.stop()