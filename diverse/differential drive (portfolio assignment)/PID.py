from machine import Pin
from machine import ADC
from utime import sleep
import time

class PID:
    def __init__(self, kp, ki, kd, target, ldrleft, ldrmiddle, ldrright ):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.target = target
        self.last_check = time.ticks_ms()
        self.integral = 0.0
        self.previous_error = 0.0
        self.left_sensor = ldrleft
        self.right_sensor = ldrright
        self.center_sensor = ldrmiddle

    def get_sensor_output(self, sensor):
        return sensor.read_u16() >> 6
    
    def deviance(self):

        left_weight = self.get_sensor_output(self.left_sensor)
        center_weight = self.get_sensor_output(self.center_sensor)
        right_weight = self.get_sensor_output(self.right_sensor)
   

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






