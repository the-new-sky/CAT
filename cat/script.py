#!/usr/bin/env python3
# coding: utf-8

__all__ = ['Script']


class Script:
    """
    Piece of code executed when an answer matches a pattern
    """

    __slots__ = ['fn', 'listeners', 'pattern']

    def __init__(self, fn: callable, pattern, listeners: list=()):
        """
        :param fn:        Callable object executed when a
                          listener need it.

        :param pattern:   expression on which the script
                          will be executed.
        :type pattern:    _sre.SRE_Match object

        :param listeners: List of Question objects that can
                          execute the script.
        """

        if isinstance(fn, Script):
            self.fn = fn.fn
        else:
            self.fn = fn

        self.listeners = list(listeners)
        self.pattern = pattern

    def execute(self, match):
        return self.fn(match)
