from collections import namedtuple
from enum import Enum

FailureConfig = namedtuple('FailureConfig', ['failures', 'seed'], defaults=(None)) 

Failure = namedtuple('Failure', ['src', 'dest', 'msg_type', 'round', 'prob', 'fail_type', 'val', 'attr'],
                     defaults=(None, None)) 

class FailType(Enum):
    MsgLoss = 1
    Delay = 2
    SetAttr = 3
    ByzatineNoPropose = 4
