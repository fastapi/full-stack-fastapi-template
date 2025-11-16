from enum import Enum

class KeyStrategyName(str, Enum):
    IP = "ip"
    HEADER = "header"
