from jinja2 import Template
from abc import ABC, abstractmethod
import math
from .message_utils import *

class OSCMessage(ABC):
    """ Something sendable
    """

    @abstractmethod
    def get_msg(self): pass

class ConcreteOSCMessage(OSCMessage):

    def __init__(self, msg):
        self._msg = msg

    def get_msg(self):
        return self._msg

class TemplatedOSCMessage(OSCMessage):
    """ An OSC message with bindable params
    and ability to compute values
    """

    def __init__(self, template, bindings: callable):
        self._template = template
        self._bindings = bindings

    def get_msg(self):
        return self._template.render(
            self._bindings(),
            math=math
        )





