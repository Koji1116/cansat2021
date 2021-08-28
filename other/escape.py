from other import melt
from sensor.motor import motor
from detection import stuck

def escape(t_melt=3):
    melt.down(t_melt)
    stuck.ue_jug()

if __name__ == '__main__':
    motor.setup()
    escape()