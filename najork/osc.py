from jinja2 import Template
from abc import ABC, abstractmethod
import math
from py_expression_eval import Parser, Expression
from .message_utils import *

class Message(ABC):
    """ Something sendable
    """

    @property
    @abstractmethod
    def path(self):
        pass

    @property
    @abstractmethod
    def data(self):
        pass

class ConcreteMessage(Message):

    def __init__(self, path, data):
        self._path = path
        self._data = data

    @property
    def path(self):
        return self._path

    @property
    def data(self):
        return self._data

    @path.setter
    def path(self):
        return self._path

    @data.setter
    def data(self):
        return self._data

class TemplatedMessage(Message):
    """ An OSC message with bindable params
    and ability to compute values
    """

    def __init__(self, path, data, bindings: callable):
        self._bindings = bindings
        self._expr_parser = Parser()
        self.parse()
        super().__init__(path, data)

    def parse(self):
        self._data_parsed = {
            exp: self._expr_parser.parse(exp)
            for exp in self._data
        }

#    def get_msg(self, t):
#        return self._template.render(
#            self._bindings(t),
#            math=math,
#            t=t
#        )

    @property
    def path(self):
        return self._path
        raise AttributeError("Access template path using .bind_path(t)")

    @property
    def data(self):
        raise AttributeError("Access template date using .bind_data(t)")

    @path.setter
    def path(self, new_path: str):
        self._path = new_path

    @data.setter
    def data(self, new_data: list):
        self._data = new_data
        self.parse()

    #def bind_path(self, t: float):
    #    return self.eval(self._path, t)

    def bind_data(self, t: float):
        return [
            self.eval(self._bind_data[d], t)
            for d in self._data
        ]

    def eval(self, expr: Expression, t: float):
        return expr.evaluate(self._bindings)







