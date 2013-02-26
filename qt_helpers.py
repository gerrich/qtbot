#!/usr/bin/env python

from PyQt4.QtCore import QObject, pyqtSlot

class ConsolePrinter(QObject):
    def __init__(self, parent=None):
        super(ConsolePrinter, self).__init__(parent)

    @pyqtSlot(str)
    def text(self, message):
        print message

class DataQueue(QObject):
    def __init__(self, parent=None):
        super(DataQueue, self).__init__(parent)
        self._queue = []

    @pyqtSlot(str)
    def push(self, message):
      self._queue.append(message)
    
    def data(self):
      return self._queue
    
    def clear(self):
      self._queue = []


