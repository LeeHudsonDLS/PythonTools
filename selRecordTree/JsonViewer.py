import argparse
import collections
import json
import sys

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

from JsonView import JsonView

class JsonViewer(QtWidgets.QMainWindow):

    def __init__(self,data,jsonLevels):
        super(JsonViewer, self).__init__()

        json_view = JsonView(data)

        self.setCentralWidget(json_view)
        self.setWindowTitle("JSON Viewer")
        self.setFixedSize(400+(jsonLevels*80),800)
        self.show()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()