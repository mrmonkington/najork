from jinja2 import Template
from abc import ABC, abstractmethod
import math
from py_expression_eval import Parser, Expression
from .message_utils import *

class Message(ABC):
    """ Something sendable
    """

    @abstractmethod
    def get_path(self, t: float):
        pass

    @abstractmethod
    def get_data(self, t: float):
        pass

class ConcreteMessage(Message):

    def __init__(self, path, data):
        self._path = path
        self._data = data

    def get_path(self, t: float):
        return self._path

    def get_data(self, t: float):
        return self._data

    def set_path(self, new: str):
        self._path = new

    def set_data(self, new_data: list):
        self._data = new_data


class TemplatedMessage(ConcreteMessage):
    """ An OSC message with bindable params
    and ability to compute values
    """

    def __init__(self, path, data, bindings: callable):
        self._bindings = bindings
        self._expr_parser = Parser()
        super().__init__(path, data)

        self._parse()

    def _get_bindings(self, t: float):
        extra = self._bindings(t)
        extra["t"] = t
        return extra

    def _parse(self):
        self._data_parsed = {
            exp: self._expr_parser.parse(exp)
            for exp in self._data
        }

    def set_data(self, new_data: list):
        self._data = new_data
        self._parse()

    def get_data(self, t: float):
        """ Get data expressions evaluated using curret @'t' input
        values, in the order the expressions were registered
        """
        return [
            self._eval(self._data_parsed[d], t)
            for d in self._data
        ]

    def _eval(self, expr: Expression, t: float):
        return expr.evaluate(self._get_bindings(t))







