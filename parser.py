# -*- coding: utf-8 -*-
import re

class EpisodeParser(object):
    """Episode Parser"""
    def __init__(self, options=None):
        """init
        Arguments:
        - `options`: parser options
        """
        self._options = options
        self._parser_exps = [
            # ex: Show.Name.S01E01...
            re.compile('(?P<showname>.+)\.S(?P<season>\d+)E(?P<episode>\d+)')
            ]
    def parse(self, filename):
        """main parse function
        returns (Show Name, Season No, Episode No)

        Arguments:
        - `filename`: file name
        """
        for exp in self._parser_exps:
            match = exp.match(filename)
            if match:
                return (match.group('showname').replace('.', ' '),
                        match.group('season'),
                        match.group('episode'))

        #if it doesn't match anything
        return ('', 0, 0)
