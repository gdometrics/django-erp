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
__version__ = '0.0.1'

from django.conf.urls import *
from django.conf import settings
from django.db.models.loading import cache

# Workaround for Django's ticket #10405.
# See http://code.djangoproject.com/ticket/10405#comment:10 for more info.
if not cache.loaded:
    cache.get_models()

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
    """ Auto discover urls of installed applications.
    """
    global LOADING
    if LOADING:
        return
    
    LOADING = True

    import imp
    
    for app in settings.INSTALLED_APPS:
        if app.startswith('django.'):
            continue
            
        # Step 1: find out the app's __path__.
        try:
            app_path = __import__(app, {}, {}, [app.split('.')[-1]]).__path__
        except AttributeError:
            continue

        # Step 2: use imp.find_module to find the app's urls.py.
        try:
            imp.find_module('urls', app_path)
        except ImportError:
            continue

        # Step 3: return the app's url patterns.
        pkg, sep, name = app.rpartition('.')
        global urlpatterns
        urlpatterns += patterns("", (r'^', include('%s.urls' % app)))
        
    LOADING = False

autodiscover()
