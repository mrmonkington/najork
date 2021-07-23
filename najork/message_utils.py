import math

def rot2rad(rot: float) -> float:
    """ Convert whole rotations to radians
    """
    return rot * 2 * math.pi

def rad2rot(rad: float) -> float:
    """ Convert radians to whole rotations
    """
    return rad / 2 / math.pi
