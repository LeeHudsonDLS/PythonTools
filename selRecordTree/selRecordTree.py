#!/usr/bin/env python3

__author__ = "Ashwin Nanjappa"

# GUI viewer to view JSON data as tree.
# Ubuntu packages needed:
# python3-pyqt5

# Std
import argparse
import collections
import json
import sys

# External
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

from JsonViewer import JsonViewer
from SelJsonHelper import SelJsonHelper





def main():
    qt_app = QtWidgets.QApplication(sys.argv)


    jsonHelper = SelJsonHelper(sys.argv[1:])

    test = jsonHelper.getDict()

    json_viewer = JsonViewer(test,jsonHelper.maxLevel)
    sys.exit(qt_app.exec_())


if "__main__" == __name__:
    main()