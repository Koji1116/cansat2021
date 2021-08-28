from parts.other import melt
from parts.sensor.motor import motor
from parts.detection import stuck


def escape(t_melt=3):
    melt.down(t_melt)
    stuck.ue_jug()

if __name__ == '__main__':
    motor.setup()
    escape()