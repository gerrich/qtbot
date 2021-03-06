#! /usr/bin/env python

import sys
from PyQt4.QtCore import QObject, pyqtSlot, QTimer
from PyQt4.QtGui import QApplication
from PyQt4.QtWebKit import QWebView
from qt_helpers import * 

html = """
<html>
<body>
    <h1>Hello!</h1><br>
    <h2><a href="#" onclick="printer.text('Message from QWebView')">QObject Test</a></h2>
    <h2><a href="#" onclick="alert('Javascript works!')">JS test</a></h2>
</body>
</html>
"""

if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = QWebView()
    frame = view.page().mainFrame()
    view.setHtml(html)
    
    printer = ConsolePrinter()
    frame.addToJavaScriptWindowObject('printer', printer)
    
    data_queue = DataQueue()
    frame.addToJavaScriptWindowObject('data_queue', data_queue)

#    frame.evaluateJavaScript("alert('Hello');")
    frame.evaluateJavaScript("printer.text('Goooooooooo!');")

    jquey_mini = open('jquery-latest.min.js', 'r').read()
    frame.evaluateJavaScript(jquey_mini)
  
    frame.evaluateJavaScript("""$("a").each(function(i,e){data_queue.push($(e).text());})""") 
    print data_queue.data()

    frame.evaluateJavaScript('window.close()')

    view.show()
   
    timer = QTimer()
    timer.timeout.connect(exit(1))
    timer.start(200)
    
    app.exec_()

    timer.stop();
    
