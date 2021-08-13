from najork.osc import ConcreteMessage, TemplatedMessage
import pytest

def test_concrete():
    c = ConcreteMessage("/bums/", [1,2,"monk"])
    assert c.path
