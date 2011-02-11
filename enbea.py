#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from os import path
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from parsers import EpisodeParser
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
        self.table_data.append((name, newname))
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
        self.model.add(filename, dirname)
        self.episodeInfos.append(info)
        if info[0]:
            self.shows.add(info[0])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = enbea()
    window.show()
    sys.exit(app.exec_())
