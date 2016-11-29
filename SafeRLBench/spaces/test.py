"""Tests for spaces module."""
from __future__ import absolute_import

from functools import partial
import inspect

from numpy import array
import SafeRLBench.spaces as spaces


"""Dictionary storing initialization arguments for classes."""
class_arguments = {
    spaces.BoundedSpace: [array([-1, -2]), array([1, 0])],
    spaces.RdSpace: [(3, 2)]
}


class TestSpaces(object):
    """
    Wrap spaces tests.

    Note that you really dont want to inherit from unittest.TestCase here,
    because it will break reasonable output with verbose testing.
    """

    classes = []

    @classmethod
    def setupClass(cls):
        """Initializes classes list."""
        for name, c in inspect.getmembers(spaces):
            if inspect.isclass(c):
                cls.classes.append(c)

    def exhaustive_tests(self):
        """Check if initial values for all classes are defined."""
        for c in self.classes:
            if c not in class_arguments:
                assert(False)

    def generate_tests(self):
        """Generate tests for spaces implementations."""
        for c in self.classes:
            if c in class_arguments:
                check = partial(self.check_contains)
                check.description = "Test implmemetation of " + c.__name__
                yield check, c

    def check_contains(self, c):
        """Check if contains and element is implemented."""
        space = c(*class_arguments[c])
        try:
            x = space.element()
            b = space.contains(x)
        except NotImplementedError:
            assert(False)
        assert(b)