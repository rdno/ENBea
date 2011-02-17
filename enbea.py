#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from os import path
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from enbea.parsers import EpisodeParser
from enbea.parsers import IMDbApiParser
from enbea.ui_main import Ui_main
from enbea.utils import renameFile

class EpisodeTableModel(QAbstractTableModel):
    """Episode Table Model"""
    def __init__(self, table_data, parent=None, *args):
        """init"""
        QAbstractTableModel.__init__(self, parent, *args)
        self.table_data = table_data
        self.header_data = ['Original Name', 'New Name']
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
        self.ui.infoLabel.setText("Add files")
        self.ui.nameMask.setText("%season%episode - %name")
        self.selectedRows = []
        self.connect_signals()
    def connect_signals(self):
        #ui stuff (buttons)
        self.connect(self.ui.browseBtn,
                     SIGNAL('clicked()'), self.openFileDialog)
        self.connect(self.ui.renameBtn,
                     SIGNAL('clicked()'), self.renameAll)
        #ui stuff (lineEdits)
        self.connect(self.ui.nameMask,
                     SIGNAL('textEdited(QString)'), self.updateNewNames)
        self.connect(self.ui.showName,
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
                done = renameFile(self.episodeInfos[row]['dir'],
                                oldname, newname)
                if done:
                    self.ui.infoLabel.setText("Renamed %s to %s." \
                                                 % (oldname, newname))
                else:
                    self.ui.infoLabel.setText("Couldn't renamed %s." \
                                                  % oldname)
    def addedToQueue(self, show):
        self.ui.infoLabel.setText("%s list added to download queue." \
                                      % show)
    def updateDownloadProgress(self, bytes):
        self.ui.progressBar.setValue(bytes)
    def startDownloadProgress(self, total, show):
        self.ui.infoLabel.setText("Downloading %s episode list" % show)
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
    def showInfoChanged(self):
        for row in self.selectedRows:
            show = str(self.ui.showName.text())
            self.episodeInfos[row]['show'] = show
            self.api_parser.addShow(show)
            print row, show
            #TODO: season and episode no change
    def episodeSelected(self):
        indexes = self.ui.episodeList.selectionModel().selectedIndexes()
        if len(indexes) == 2: #one row contains two columns
            row = indexes[0].row()
            self.selectedRows = [row]
            self.ui.showProperties.show()
            self.ui.showName.setDisabled(False)
            self.ui.seasonNo.setDisabled(False)
            self.ui.episodeNo.setDisabled(False)
            self.ui.showName.setText(self.episodeInfos[row]['show'])
            self.ui.seasonNo.setText(str(self.episodeInfos[row]['season']))
            self.ui.episodeNo.setText(str(self.episodeInfos[row]['episode']))
        elif len(indexes) > 2:
            #TODO:support for multiple edit
            self.ui.showProperties.show()
            self.ui.showName.setDisabled(True)
            self.ui.seasonNo.setDisabled(True)
            self.ui.episodeNo.setDisabled(True)
        else:
            self.ui.showProperties.hide()
            self.ui.showName.setText("")
            self.ui.seasonNo.setText("")
            self.ui.episodeNo.setText("")
    def openFileDialog(self):
        fullname = QFileDialog.getOpenFileName(self, 'Open file',
                    '~')
        info = self.parser.parse(str(fullname))
        self.model.add(info['filename'], '')
        self.episodeInfos.append(info)
        if info['show']:
            self.shows.add(info['show'])
            self.api_parser.addShow(info['show'])
    def newname(self, info):
        if info['show'] == '':
            return ""
        name = self.ui.nameMask.text()
        name = name.replace("%season",  str(info['season']))
        name = name.replace("%episode",  str(info['episode']).zfill(2))
        name = name.replace("%show",  info['show'])
        name = name.replace("%name",
                            self.api_parser.getEpisodeName(info))
        return name + "." + info["extension"]
    def showNotFound(self):
        self.ui.progressBar.hide()
        self.ui.infoLabel.setText("Show list couldn't be parsed")
    def showFound(self):
        self.ui.progressBar.hide()
        self.ui.infoLabel.setText("Download Successful!")
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
