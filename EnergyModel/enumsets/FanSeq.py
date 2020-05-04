from enum import Enum

class FanSeq(Enum):
    """Fan Sequence Enumeration"""
    CONSTANT_SPEED = 0
    STAGED = 1
    VARIABLE_AIRFLOW = 2