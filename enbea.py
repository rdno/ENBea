#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from os import path
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from enbea.parsers import EpisodeParser
from enbea.parsers import IMDbApiParser
from enbea.ui_main import Ui_main
from enbea.utils import get_links
from enbea.utils import get_video_file_filter
from enbea.utils import get_videos
from enbea.utils import is_a_video_file
from enbea.utils import rename_file
from enbea.utils import set_drag_and_drop_events
from enbea.translation import i18n

class EpisodeTableModel(QAbstractTableModel):
    """Episode Table Model"""
    def __init__(self, table_data, parent=None, *args):
        """init"""
        QAbstractTableModel.__init__(self, parent, *args)
        self.table_data = table_data
        self.header_data = [i18n('Original Name'), i18n('New Name')]
    def rowCount(self, parent=QModelIndex()):
        return len(self.table_data)
    def columnCount(self,  parent=QModelIndex()):
        return len(self.header_data)
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.header_data[col])
        return QVariant()
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()
        elif role == Qt.TextColorRole:
            if self.data(self.index(index.row(), 1)) == "":
                return QVariant(QColor(Qt.red))
            else:
                return QVariant()
        elif role != Qt.DisplayRole:
            return QVariant()
        return QVariant(self.table_data[index.row()][index.column()])
    def add(self, name, newname=''):
        row = self.rowCount()
        index = self.index(row, 0)
        self.beginInsertRows(index, row, row)
        self.insertRow(row) #implement ?
        self.table_data.append([name, newname])
        self.endInsertRows()
    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and role == Qt.EditRole:
            self.table_data[index.row()][index.column()] = value
            self.dataChanged.emit(index, index)
            return True
        return False


class enbea(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.ui = Ui_main()
	myWidget = QWidget()
        self.ui.setupUi(myWidget)
	self.setCentralWidget(myWidget)
        self.setWindowTitle("ENBea")
        self._setupEpisodeList()
        self.parser = EpisodeParser()
        self.api_parser = IMDbApiParser()
        self.ui.showProperties.hide()
        self.ui.progressBar.hide()
        self.ui.infoLabel.setText(i18n("Add files"))
        self.ui.nameMask.setText(i18n("%season%episode - %name"))
        self.selectedRows = []
        self.connect_signals()
    def connect_signals(self):
        #ui stuff (buttons)
        self.connect(self.ui.addFileBtn,
                     SIGNAL('clicked()'), self.openFileDialog)
        self.connect(self.ui.addFolderBtn,
                     SIGNAL('clicked()'), self.openFolderDialog)
        self.connect(self.ui.renameBtn,
                     SIGNAL('clicked()'), self.renameAll)
        #ui stuff (lineEdits)
        self.connect(self.ui.nameMask,
                     SIGNAL('textEdited(QString)'), self.updateNewNames)
        self.connect(self.ui.showName,
                     SIGNAL('editingFinished()'), self.showInfoChanged)
        self.connect(self.ui.seasonNo,
                     SIGNAL('editingFinished()'), self.showInfoChanged)
        self.connect(self.ui.episodeNo,
                     SIGNAL('editingFinished()'), self.showInfoChanged)
        #Show state signals
        self.connect(self.api_parser, SIGNAL('ShowListUpdated()'),
                     self.showFound)
        self.connect(self.api_parser, SIGNAL('ShowNotFound()'),
                     self.showNotFound)
        #EList download signals
        self.connect(self.api_parser.downloader,
                     SIGNAL('AddedToQueue(QString)'),
                     self.addedToQueue)
        self.connect(self.api_parser.downloader,
                     SIGNAL('downloadStarted(int, QString)'),
                     self.startDownloadProgress)
        self.connect(self.api_parser.downloader,
                     SIGNAL('downloadProgress(int)'),
                     self.updateDownloadProgress)
    def renameAll(self):
        mod = self.model
        for row in range(mod.rowCount()):
            newname = str(mod.data(mod.index(row, 1)).toString())
            if newname:
                oldname = str(mod.data(mod.index(row, 0)).toString())
                done = rename_file(self.episodeInfos[row]['dir'],
                                oldname, newname)
                if done:
                    self.ui.infoLabel.setText(i18n("Renamed {0} to {1}") \
                                                 % (oldname, newname))
                else:
                    self.ui.infoLabel.setText(i18n("Couldn't renamed %s.") \
                                                  % oldname)
    def addedToQueue(self, show):
        self.ui.infoLabel.setText(i18n("%s list added to download queue.") \
                                      % show)
    def updateDownloadProgress(self, bytes):
        self.ui.progressBar.setValue(bytes)
    def startDownloadProgress(self, total, show):
        self.ui.infoLabel.setText(i18n("Downloading %s episode list") % show)
        self.ui.progressBar.setMinimum(0)
        self.ui.progressBar.setMaximum(total)
        self.ui.progressBar.show()
    def _setupEpisodeList(self):
        self.episodeFiles = []
        self.episodeInfos = []
        self.shows = set()
        self.model = EpisodeTableModel(self.episodeFiles)
        self.ui.episodeList.setModel(self.model)
        self.ui.episodeList.setColumnWidth(0, 200)
        self.ui.episodeList.setColumnWidth(1, 200)
        self.ui.episodeList.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.connect(self.ui.episodeList.selectionModel(),
                SIGNAL('selectionChanged(QItemSelection,QItemSelection)'),
                self.episodeSelected);
        set_drag_and_drop_events(self.ui.episodeList, self.drop)
    def drop(self, event):
        for link in get_links(event.mimeData()):
            if path.isdir(link):
                for video in get_videos(link):
                    self.addFile(video)
            elif is_a_video_file(link):
                self.addFile(link)

    def showInfoChanged(self):
        show = str(self.ui.showName.text())
        season = int(self.ui.seasonNo.text())
        episode = int(self.ui.episodeNo.text())
        for row in self.selectedRows:
            self.episodeInfos[row]['show'] = show
            self.api_parser.addShow(show)
            if self.ui.seasonNo.isEnabled():
                self.episodeInfos[row]['season'] = season
                self.episodeInfos[row]['episode'] = episode
        self.updateNewNames()
    def episodeSelected(self):
        indexes = self.ui.episodeList.selectionModel().selectedIndexes()
        if len(indexes) == 2: #one row contains two columns
            row = indexes[0].row()
            self.selectedRows = [row]
            self.ui.showProperties.show()
            self.ui.showName.setDisabled(False)
            self.ui.seasonNo.setDisabled(False)
            self.ui.episodeNo.setDisabled(False)
            self.ui.showName.setPlaceholderText("")
            self.ui.showName.setText(self.episodeInfos[row]['show'])
            self.ui.seasonNo.setText(str(self.episodeInfos[row]['season']))
            self.ui.episodeNo.setText(str(self.episodeInfos[row]['episode']))
        elif len(indexes) > 2:
            for index in indexes:
                self.selectedRows.append(index.row())
            self.selectRows = set(self.selectedRows)
            firstRow = indexes[0].row()
            self.ui.showProperties.show()
            self.ui.showName.setPlaceholderText(i18n("Multiple Edit is on"))
            self.ui.showName.setText("")
            self.ui.showName.setDisabled(False)
            self.ui.seasonNo.setDisabled(True)
            self.ui.episodeNo.setDisabled(True)
        else:
            self.ui.showProperties.hide()
            self.ui.showName.setText("")
            self.ui.seasonNo.setText("")
            self.ui.episodeNo.setText("")
            self.ui.showName.setPlaceholderText("")
    def addFile(self, fullname):
        info = self.parser.parse(str(fullname))
        self.model.add(info['filename'], '')
        self.episodeInfos.append(info)
        if info['show']:
            self.shows.add(info['show'])
            self.api_parser.addShow(info['show'])
    def openFileDialog(self):
        fullnames = QFileDialog.getOpenFileNames(self, i18n("Open file"),
                    '~', filter=get_video_file_filter()
                                + ";;"+i18n("All Files")+" (*)")
        for fullname in fullnames:
            self.addFile(fullname)
    def openFolderDialog(self):
        dirname = QFileDialog.getExistingDirectory(self, i18n("Select folder"),
                                                   '~')
        for video in get_videos(str(dirname)):
            self.addFile(video)
    def newname(self, info):
        if info['show'] == '' or info['season'] == 0 or \
                info['episode'] == 0:
            return ""
        episodeName = self.api_parser.getEpisodeName(info)
        if episodeName == '':
            return ""
        name = self.ui.nameMask.text()
        name = name.replace(i18n("%season"),  str(info['season']))
        name = name.replace(i18n("%Season"),  str(info['season']).zfill(2))
        name = name.replace(i18n("%episode"),  str(info['episode']).zfill(2))
        name = name.replace(i18n("%show"),  info['show'])
        name = name.replace(i18n("%name"), episodeName)
        return name + "." + info['extension']
    def showNotFound(self):
        self.ui.progressBar.hide()
        self.ui.infoLabel.setText(i18n("Show list couldn't be parsed"))
    def showFound(self):
        self.ui.progressBar.hide()
        self.ui.infoLabel.setText(i18n("Download Successful!"))
        self.updateNewNames()
    def updateNewNames(self):
        mod = self.model
        for row in range(mod.rowCount()):
            index = mod.index(row, 1)
            mod.setData(index, self.newname(self.episodeInfos[row]))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = enbea()
    window.show()
    sys.exit(app.exec_())
