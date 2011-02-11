# -*- coding: utf-8 -*-
import json
import re
import urllib
from utils import camelCase

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
                return (camelCase(match.group('showname').replace('.', ' ')),
                        match.group('season'),
                        match.group('episode'))

        #if it doesn't match anything
        return ('', 0, 0)
class IMDbApiParser(object):
    """IMDbApi Parser (http://imdbapi.poromenos.org/)"""
    def __init__(self):
        """init"""
        self._episodeList = {}

    def getEpisodeList(self, show):
        return self._episodeList[show]
    def getEpisodeName(self, episodeInfo):
        show = episodeInfo[0]
        season = int(episodeInfo[1])
        episode = int(episodeInfo[2])
        if show:
            return self._episodeList[show][(season, episode)]
        return ""
    def getShowList(self):
        return self._episodeList.keys()
    def addShow(self, show):
        url = 'http://imdbapi.poromenos.org/js/?name=%s'
        data = json.load(urllib.urlopen(url % show))
        self._episodeList[show] = {}
        if data or not 'show' in data:
            episodes = data[data.keys()[0]]["episodes"]
            for episode in episodes:
                self._episodeList[show][(episode['season'],
                                   episode['number'])] = episode['name']

            return True
        return False
