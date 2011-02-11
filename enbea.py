#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from os import path
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from parsers import EpisodeParser
from parsers import IMDbApiParser
from main_ui import Ui_main

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
    def data(self, index, role):
        if not index.isValid():
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

        self.connect(self.ui.browseBtn,
                     SIGNAL('clicked()'), self.openFileDialog)
        self._setupEpisodeList()
        self.parser = EpisodeParser()
        self.api_parser = IMDbApiParser()
        self.connect(self.api_parser, SIGNAL('ShowListUpdated()'),
                     self.updateNewNames)
        self.connect(self.api_parser, SIGNAL('ShowNotFound()'),
                     self.showNotFound)

        self.ui.progressBar.hide()
        self.ui.infoLabel.setText("Add files")
        self.connect(self.api_parser.downloader,
                     SIGNAL('downloadStarted(int, QString)'),
                     self.startDownloadProgress)
        self.connect(self.api_parser.downloader,
                     SIGNAL('downloadProgress(int)'),
                     self.updateDownloadProgress)
        self.ui.nameMask.setText("%season%episode - %name")
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
    def episodeSelected(self):
        indexes = self.ui.episodeList.selectionModel().selectedIndexes()
        if len(indexes) > 0:
            row = indexes[0].row()
            self.ui.showName.setText(self.episodeInfos[row][0])
        else:
            self.ui.showName.setText("")
    def openFileDialog(self):
        fullname = QFileDialog.getOpenFileName(self, 'Open file',
                    '~')
        filename = path.basename(str(fullname))
        dirname = path.dirname(str(fullname))
        info = self.parser.parse(filename)
        self.model.add(filename, '')
        self.episodeInfos.append(info)
        if info[0]:
            self.shows.add(info[0])
            self.api_parser.addShow(info[0])
    def newname(self, info):
        name = self.ui.nameMask.text()
        name = name.replace("%season",  info[1])
        name = name.replace("%episode",  info[2])
        name = name.replace("%show",  info[0])
        name = name.replace("%name",
                            self.api_parser.getEpisodeName(info))
        return name
    def showNotFound(self):
        self.ui.progressBar.hide()
        self.ui.infoLabel.setText("Show list couldn't be parsed")
    def updateNewNames(self):
        self.ui.progressBar.hide()
        self.ui.infoLabel.setText("Download Successful!")
        mod = self.model
        for row in range(mod.rowCount()):
            index = mod.index(row, 1)
            mod.setData(index, self.newname(self.episodeInfos[row]))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = enbea()
    window.show()
    sys.exit(app.exec_())
