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

import types

class _PluggetCache(object):
    def __init__(self):
        self.__discovered = False
        self.__sources = {}
        
    def register(self, func, default_template = "pluggets/base_plugget.html", context = {}):
        """Register a new plugget source.
        """
        if isinstance(func, types.FunctionType):
            import inspect
            module_name = inspect.getmodule(func)
            uid = "%s.%s" % (module_name, func)
            title, sep, description = inspect.getdoc(func).partition("\n")
            self.__sources[uid] = {"title": title, "description": description, "default_template": default_template, "context": context}

    def get_display_sources(self):
        """Returns the list of the registered plugget sources, usable in a form.
        """
        dsources = {}
        for s in self.sources.items():
            dsources[s.title] = {"uid": s.uid, "description": s.description, "default_template": s.default_template, "context": s.context}
        return dsources

    def __get_sources(self):
        self.__discover_pluggets()
        return self.__sources
    sources = property(__get_sources)

    def __discover_pluggets(self):        
        if self.__discovered:
            return
            
        from django.conf import settings
            
        # Import default pluggets.
        import base
        
        for app in settings.INSTALLED_APPS:
            # Skip Django's apps.
            if app.startswith('django'):
                continue
                
            # Try to import pluggets from the current app. 
            try:
                module_name = "%s.pluggets" % app
                module = __import__(module_name, {}, {}, ['*'])
            except ImportError:
                pass
                
        self.__discovered = True 

registry = _PluggetCache()
