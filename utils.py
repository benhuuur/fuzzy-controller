import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


class PID:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral = 0
        self.previous_error = 0

    def compute(self, target, current, delta):
        error = target - current
        self.integral += error * delta

        derivative = (error - self.previous_error) / delta
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        self.previous_error = error
        return output

def grid(W, H, L, resolution):
    nx = int(W / resolution)
    ny = int(H / resolution)
    nz = int(L / resolution)
    return nx, ny, nz
