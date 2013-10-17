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

from base import *

# Auto-discovering of application specific settings.
for app in INSTALLED_APPS:

    if app.startswith("django."):
        continue

    app_settings = None

    # 1) Try to import app settings from the current package.
    try:
        prefix, sep, app_name = app.rpartition('.')
        app_settings = __import__(app_name, globals(), locals(), ['*'], 1)
    
    # 2) If fails, try to import settings from app settings module.
    except:
        try:
          app_settings = __import__('%s.settings' % app, globals(), locals(), ['*'], 0)
        except:
          continue

    for attr in dir(app_settings):
        if not attr.startswith('_'):
            globals()[attr] = getattr(app_settings, attr)
