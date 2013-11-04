#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This file is part of the django ERP project.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

__author__ = 'Emanuele Bertoldi <emanuele.bertoldi@gmail.com>'
__copyright__ = 'Copyright (c) 2013 Emanuele Bertoldi'
__version__ = '0.0.2'

from django.conf.urls import *
from django.conf import settings

# Basic URL patterns bootstrap.
urlpatterns = patterns('',)

if 'django.contrib.admin' in settings.INSTALLED_APPS:
  from django.contrib import admin
  admin.autodiscover()
  urlpatterns += patterns('', (r'^admin/', include(admin.site.urls)))
  if 'django.contrib.admindocs' in settings.INSTALLED_APPS:
    urlpatterns += patterns('', (r'^admin/doc/', include('django.contrib.admindocs.urls')))

if 'django.contrib.staticfiles' in settings.INSTALLED_APPS:
  from django.contrib.staticfiles.urls import staticfiles_urlpatterns
  urlpatterns += staticfiles_urlpatterns()

# Application specific URL patterns discovering.
LOADING = False

def autodiscover():
    """ Auto discover urls and signals of installed applications.
    """
    global LOADING
    if LOADING:
        return
    
    LOADING = True
    
    for app in settings.INSTALLED_APPS:
        if app.startswith('django.'):
            continue

        # Step 1: import URLs.
        try:
            urls = __import__("%s.urls" % app, {}, {}, ["*"])
            global urlpatterns
            urlpatterns += patterns("", (r'^', include('%s.urls' % app)))
        except ImportError:
            pass
            
        # Step 2: import signals logic.
        try:
            signals = __import__("%s.signals" % app, {}, {}, ["*"])
        except ImportError:
            pass
        
    LOADING = False

autodiscover()
