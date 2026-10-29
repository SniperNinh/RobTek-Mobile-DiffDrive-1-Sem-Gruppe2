from machine import Pin
from machine import ADC
from utime import sleep
import time

class PID:
    def __init__(self, kp, ki, kd, target):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.target = target
        self.last_check = time.ticks_ms()
        
        self.integral = 0.0
        self.previous_error = 0.0

    def PID_update(self, deviance):
        now = time.ticks_ms()
        dt = now - self.last_check
        self.last_check = now
        if dt <= 0:
            return 0

        error = self.target - deviance
        

        
        P = self.kp * error
        self.integral += error  * dt
        I = self.integral * self.ki
        dy = (error - self.previous_error) / dt
        D =  self.kd * dy

        self.previous_error = error

        return P+I+D



pid = PID(
    kp = 0,
    ki = 0,
    kd = 0,
    target = 0
)

left_sensor = ADC(26)
right_sensor = ADC(28)
center_sensor = ADC(27)

def get_sensor_output(sensor):
    return sensor.read_u16() >> 6

def deviance():

    left_weight = get_sensor_output(left_sensor)
    center_weight = get_sensor_output(center_sensor)
    right_weight = get_sensor_output(right_sensor)
   

    total = left_weight + center_weight + right_weight

    if total > 0:
        deviance = (
            left_weight * -1 +
            center_weight * 0 +
            right_weight * 1 
         ) / total
    else:
        deviance = 0

    return deviance

while True:
    position = 0- deviance()
    correction = pid.PID_update(deviance())
    print(correction, deviance())
    sleep(0.1)
