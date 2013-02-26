#! /usr/bin/env python

from PyQt4.QtCore import *
from PyQt4.QtWebKit import *
from PyQt4.QtGui import *
from PyQt4.QtScript import *
import sys
import time

currentfile = "test.htm"
app = QApplication(sys.argv)
web = QWebView()
web.load(QUrl("http://news.google.com"))
web.show()
data =  web.page().currentFrame().documentElement().toInnerXml()
open(currentfile,"w").write(data)
sys.exit(app.exec_())
