# -*- coding: utf-8 -*-
import json
import re
import urllib
import urllib2
from os import path
from PyQt4.QtCore import QObject
from PyQt4.QtCore import QThread
from PyQt4.QtCore import SIGNAL
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
            re.compile('(?P<showname>.+)\.S(?P<season>\d+)E(?P<episode>\d+)', re.IGNORECASE)
            ]
        self._episode_only_exps = [
            #ex: S01E01
            re.compile('.*S(?P<season>\d+)E(?P<episode>\d+).*', re.IGNORECASE),
            #ex: 01x01
            re.compile('.*(?P<season>\d+)x(?P<episode>\d+).*')]
    def parse(self, fullname):
        """main parse function
        returns (Show Name, Season No, Episode No)

        Arguments:
        - `fullname`: /path/to/file
        """
        filename = path.basename(fullname)
        dirname = path.dirname(fullname)
        extension = filename.split(".")[-1]
        for exp in self._parser_exps:
            match = exp.match(filename)
            if match:
                return {'show':camelCase(match.group('showname').replace('.', ' ')),
                        'season':int(match.group('season')),
                        'episode':int(match.group('episode')),
                        'filename':filename,
                        'dir':dirname,
                        'extension':extension}
        #if showname couldn't found try season & episode no only
        for exp in self._episode_only_exps:
            match = exp.match(filename)
            if match:
                return {'show':'',
                        'season':int(match.group('season')),
                        'episode':int(match.group('episode')),
                        'filename':filename,
                        'dir':dirname,
                        'extension':extension}
        #if it doesn't match anything
        return {'filename':filename,
                'dir':dirname,
                'extension':extension,
                'show':'',
                'season':0,
                'episode':0}
class IMDbApiParser(QObject):
    """IMDbApi Parser (http://imdbapi.poromenos.org/)"""
    def __init__(self):
        """init"""
        QObject.__init__(self)
        self._episodeList = {}
        self.downloader = EListDownloader()
        self.connect(self.downloader,
                     SIGNAL('EListDownloaded'),
                     self._downloaded)
    def getEpisodeList(self, show):
        return self._episodeList[show]
    def getEpisodeName(self, episodeInfo):
        try:
            if episodeInfo['show']:
                show = episodeInfo['show']
                season = int(episodeInfo['season'])
                episode = int(episodeInfo['episode'])
                return self._episodeList[show][(season, episode)]
        except KeyError:
            return ""
        return ""
    def getShowList(self):
        return self._episodeList.keys()
    def addShow(self, show):
        if self._episodeList.has_key(show):
            return True
        self.downloader.addToQueue(show)
        if not self.downloader.isRunning():
            self.downloader.start()
    def _downloaded(self, show, data):
        if data:
            if not 'show' in data:
                self._episodeList[show] = {}
                episodes = data[data.keys()[0]]["episodes"]
                for episode in episodes:
                    self._episodeList[show][(int(episode['season']),
                                             int(episode['number']))] = episode['name']
                self.emit(SIGNAL("ShowListUpdated()"))
            else:
                self.emit(SIGNAL("ShowNotFound()"))

class EListDownloader(QThread):
    """Episode List Downloader"""
    def __init__(self):
        QThread.__init__(self)
        self._queue = []
        self.url = 'http://imdbapi.poromenos.org/js/'
    def geturl(self, show):
        return self.url + '?'+ urllib.urlencode({'name':show})
    def addToQueue(self, show):
        self._queue.append(show)
    def run(self):
        while self._queue:
            show = self._queue.pop(0)
            self.emit(SIGNAL('AddedToQueue(QString)'), show)
            response = urllib2.urlopen(self.geturl(show))
            bytes, data = self.chunk_read(response, show)
            data = json.loads(data)
            self.emit(SIGNAL('EListDownloaded'),
                      show, data)
    def chunk_read(self, response, show):
        total_size = response.info().getheader('Content-Length').strip()
        total_size = int(total_size)
        self.emit(SIGNAL('downloadStarted(int, QString)'),
                  total_size, show)
        chunk_size = 1024
        bytes = 0
        data = ''
        while 1:
            chunk = response.read(chunk_size)
            bytes += len(chunk)
            data += chunk
            self.emit(SIGNAL('downloadProgress(int)'),
                      bytes)
            if not chunk:
                break
        return bytes, data
