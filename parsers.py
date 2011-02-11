# -*- coding: utf-8 -*-
import json
import re
import urllib
import urllib2
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
        show = episodeInfo[0]
        season = int(episodeInfo[1])
        episode = int(episodeInfo[2])
        if show:
            return self._episodeList[show][(season, episode)]
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
def chunk_report(bytes_so_far, chunk_size, total_size):
   percent = float(bytes_so_far) / total_size
   percent = round(percent*100, 2)
   print "Downloaded %d of %d bytes (%0.2f%%)" % (bytes_so_far, total_size, percent)

def chunk_read(response, chunk_size=1024, report_hook=None):
    total_size = response.info().getheader('Content-Length').strip()
    total_size = int(total_size)
    bytes_so_far = 0
    chunks = ""
    while 1:
        chunk = response.read(chunk_size)
        bytes_so_far += len(chunk)
        chunks += chunk

        if not chunk:
            break

        if report_hook:
            report_hook(bytes_so_far, chunk_size, total_size)

    return bytes_so_far, chunks
