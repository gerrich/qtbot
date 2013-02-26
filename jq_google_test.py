#! /usr/bin/env python

import sys
from PyQt4.QtCore import QObject, pyqtSlot, QTimer, QString, QUrl
from PyQt4.QtGui import QApplication
from PyQt4.QtWebKit import QWebView
from qt_helpers import * 

import urllib


def get_google_search_url(query):
  url_query = urllib.quote(query)
  return """http://www.google.ru/#sclient=psy-ab&hl=ru&newwindow=1&source=hp&pbx=1&aq=f&aqi=&aql=&gs_sm=s&q=%s&oq=%s"""\
      %(url_query, url_query)

def get_mail_search_url(query):
  url_query = urllib.quote(query)
  return "http://go.mail.ru/search?fr=main&rch=e&q=%s"%url_query

def get_yandex_search_url(query):
  url_query = urllib.quote(query)
  return "http://yandex.ru/yandsearch?text=%s&lr=213"%url_query



class Googler(QObject):
  def __init__(self):
    super(Googler, self).__init__()

  def query(self, query_text):
    self.timer = QTimer()
    
    url = get_mail_search_url(query_text)

    self.app = QApplication(sys.argv)
    self.view = QWebView()
    self.frame = self.view.page().mainFrame()
    print url
    self.view.load(QUrl(QString(url)))

    self.view.loadStarted.connect(self.loadStarted)
    self.view.loadProgress.connect(self.loadProgress)
    self.view.loadFinished.connect(self.loadFinished)

    self.view.show()

    self.app.exec_()
 
  def loadStarted(self):
    print "loadStarted"

  def loadProgress(self):
    print "loadProgress"

  def loadFinished(self):
    print "loadFinished"

    self.timer.singleShot(100, self.parse_serp)

  def inject_jquery(self):
    jquey_mini = open('jquery-latest.min.js', 'r').read()
    frame.evaluateJavaScript(jquey_mini)

  """
  def schedule_action(self, timeout, action):
    self.timer.timeout.connect(action)
    self.timer.start(timeout)

  def stop_timer(self):
    self.timer.stop()
  """

  def parse_serp(self):
    self.parse_mail()
    
    self.timer.singleShot(100, self.close_app)

  def parse_yandex(self):
    data_queue = DataQueue()
    self.frame.addToJavaScriptWindowObject('data_queue', data_queue)

    self.frame.evaluateJavaScript("""
$('.b-head-logo__text').contents().each(function(i,e){data_queue.push($(e).text());})
    """)
    print " ".join([str(i.toUtf8()).decode("utf8") for i in data_queue.data()])
    data_queue.clear()

    self.frame.evaluateJavaScript("""
$('li.b-serp-item a.b-serp-item__title-link').each(function(i,e){data_queue.push($(e).text());})
    """) 
    title_list = [str(i.toUtf8()).decode("utf8") for i in data_queue.data()]
    print "\n".join(title_list)
      

  def parse_mail(self):
    data_queue = DataQueue()
    self.frame.addToJavaScriptWindowObject('data_queue', data_queue)
    
    self.frame.evaluateJavaScript("""
$('html head title').each(function(i,e){data_queue.push($(e).text());})
    """)

    title_str = " ".join([str(i.toUtf8()).decode("utf8") for i in data_queue.data()])
    data_queue.clear()

    print title_str

    self.frame.evaluateJavaScript("""
$('ul.res-list > li .res-head a').each(function(i,e){data_queue.push($(e).text());})
    """) 
    title_list = [str(i.toUtf8()).decode("utf8") for i in data_queue.data()]
    print "\n".join(title_list)

  def close_app(self):
    self.app.exit(0)

if __name__ == '__main__':

    googler = Googler()

    googler.query("jquery firebug")
  
    sys.exit(0)

#    frame.evaluateJavaScript('alert(1)')

    data_queue = DataQueue()
    frame.addToJavaScriptWindowObject('data_queue', data_queue)

  
    frame.evaluateJavaScript("""
$('li div h3').each(function(i,e){data_queue.push($(e).text());})
    """) 
    print data_queue.data()

    frame.evaluateJavaScript('window.close()')

    """   
    timer = QTimer()
    timer.timeout.connect(exit(1))
    timer.start(200)
    
    app.exec_()

    timer.stop();
    """    
    
