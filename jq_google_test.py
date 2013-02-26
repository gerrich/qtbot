#! /usr/bin/env python
# -*- coding: utf8 -*-

import sys
from PyQt4.QtCore import QObject, pyqtSlot, QTimer, QString, QUrl
from PyQt4.QtGui import QApplication
from PyQt4.QtWebKit import QWebView
from qt_helpers import * 

import urllib
import re

import codecs
import ujson

def get_search_url(query, engine):
  url_query = urllib.quote(query)
  if engine == 'mail':
    return "http://go.mail.ru/search?fr=main&rch=e&q=%s"%url_query
  elif engine == 'yandex':
    return "http://yandex.ru/yandsearch?text=%s&lr=213"%url_query
  elif engine == 'google':
    return """http://www.google.ru/#sclient=psy-ab&hl=ru&newwindow=1&source=hp&pbx=1&aq=f&aqi=&aql=&gs_sm=s&q=%s&oq=%s"""\
        %(url_query, url_query)
  else:
    return None

class Googler(QObject):
  def __init__(self):
    super(Googler, self).__init__()

  def query(self, query_text, engine):
    self.context = {}

    self.timer = QTimer()
    self.is_loaded = False

    url = get_search_url(query_text, engine)

    self.app = QApplication(sys.argv)
    self.view = QWebView()
    self.frame = self.view.page().mainFrame()
    #print url
    self.view.load(QUrl(QString(url)))

    self.view.loadStarted.connect(self.loadStarted)
    self.view.loadProgress.connect(self.loadProgress)
    self.view.loadFinished.connect(self.loadFinished)

    self.view.show()
    
    self.timer.singleShot(5000, self.die)

    status = self.app.exec_()

    if status:
      return None
    else:
      return self.context


  def loadStarted(self):
#    print "loadStarted"
    self.is_loaded = False
    
  
  def loadProgress(self):
#    print "loadProgress"
    self.is_loaded = False

  def loadFinished(self):
#    print "loadFinished"
    self.is_loaded = True
    self.timer.singleShot(100, self.parse_serp)

  def inject_jquery(self):
    jquey_mini = open('jquery-latest.min.js', 'r').read()
    self.view.page().mainFrame().evaluateJavaScript(jquey_mini)

  def get_html(self):
    return self.view.page().mainFrame().toHtml()

  def parse_serp(self):
    if not self.is_loaded:
      return None

    host = self.view.url().host()
    if host == 'go.mail.ru':
      self.parse_mail()
    elif host == 'yandex.ru':
      self.parse_yandex()
    elif host == 'www.google.ru':
      self.google_try_count = 0
      self.try_parse_google()
    #else:
    #  print "bad host"
    self.timer.singleShot(100, self.close_app)

  def try_parse_google(self):
    self.google_try_count += 1

    items = self.frame.findAllElements('#foot')
    
    if items.count() > 0:
      self.parse_google()

    else:  
      if self.google_try_count > 10:
        print "exceeded max attempt count"
        return None
      else:
        self.timer.singleShot(100, self.try_parse_google)
  
  def parse_google(self):
    print "parsing google serp.."
    self.inject_jquery()
    
    data_queue = DataQueue()
    self.frame.addToJavaScriptWindowObject('data_queue', data_queue)

    #self.view.page().mainFrame().evaluateJavaScript('data_queue.push(typeof(jQuery))')
    
    self.frame.evaluateJavaScript("""
$('div#resultStats').each(function(i,e){data_queue.push($(e).text());})
    """)

    title_str = " ".join([str(i.toUtf8()).decode("utf8") for i in data_queue.data()])
    data_queue.clear()

    print title_str

    self.frame.evaluateJavaScript("""
$('li.g h3.r').each(function(i,e){data_queue.push($(e).text());})
    """) 
    title_list = [str(i.toUtf8()).decode("utf8") for i in data_queue.data()]
    data_queue.clear()
    print "\n".join(title_list)
    
    self.frame.evaluateJavaScript("""
$('li.g span.st').each(function(i,e){data_queue.push($(e).text());})
    """) 
    body_list = [str(i.toUtf8()).decode("utf8") for i in data_queue.data()]
    print "\n".join(body_list)

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
    data_queue.clear()
    print "\n".join(title_list)
      
    self.frame.evaluateJavaScript("""
$('li.b-serp-item div.b-serp-item__text').each(function(i,e){data_queue.push($(e).text());})
    """) 
    title_list = [str(i.toUtf8()).decode("utf8") for i in data_queue.data()]
    data_queue.clear()
    print "\n".join(title_list)

  def parse_mail(self):
    data_queue = DataQueue()
    self.frame.addToJavaScriptWindowObject('data_queue', data_queue)
    
    self.frame.evaluateJavaScript("""
$('html head title').each(function(i,e){data_queue.push($(e).text());})
    """)

    title_str = " ".join([str(i.toUtf8()).decode("utf8") for i in data_queue.data()])
    data_queue.clear()

    count = None

    count_re = re.compile(u'\-([^\-]+)Поиск\@Mail\.Ru\s*$', re.UNICODE)
    m = count_re.search(title_str)
    if m:
      count_str = re.compile('[\s\.]+', re.UNICODE).sub(' ', m.group(1)).strip()
      count_str = re.compile('([0-9])\ ([0-9])', re.UNICODE).sub('\\1\\2', count_str)
      #print count_str

      fields = count_str.split(" ")
      if len(fields) > 1 and re.match('[0-9]+',fields[0]):
        count = int(fields[0])
        if len(fields) > 2:
          ext = fields[1].strip()
          #print ext
          if ext == u'тыс':
            count *= int(1e3)
          elif ext == u'млн':
            count *= int(1e6)
          elif ext == u'млрд':
            count *= int(1e9)
          else:
            count = None
      elif count_str == u'ничего не найдено':
        count = 0

    self.context['count'] = count

    self.frame.evaluateJavaScript("""
$('ul.res-list > li .res-head a').each(function(i,e){data_queue.push($(e).text());})
    """) 
    title_list = [str(i.toUtf8()).decode("utf8") for i in data_queue.data()]
    self.context['tile_list'] = [i.strip() for i in title_list]
    data_queue.clear()
    
    self.frame.evaluateJavaScript("""
$('ul.res-list > li div.snip').each(function(i,e){data_queue.push($(e).text());})
    """) 
    body_list = [str(i.toUtf8()).decode("utf8") for i in data_queue.data()]
    self.context['body_list'] = [re.sub('\s+',' ',i).strip() for i in body_list]
    data_queue.clear()

  def close_app(self):
    self.app.exit(0)

  def die(self):
    self.app.exit(1)

if __name__ == '__main__':

  googler = Googler()

  for line in codecs.getreader('utf8')(sys.stdin):
    query = line.strip()
    if query == '':
      next
    serp = googler.query(query, 'mail')
    if serp == None:
      serp = {'error':1}
    serp['query'] = query

    print ujson.dumps(serp)
