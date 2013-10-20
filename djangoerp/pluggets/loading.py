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

class _PluggetCache(object):
    def __init__(self):
        self.__discovered = False
        self.__sources = {}
        
    def register(self, func, title=None, description=None, template="pluggets/base_plugget.html", context={}):
        """Register a new plugget source.
        """
        if callable(func):
            import inspect
            module_name = inspect.getmodule(func)
            uid = "%s.%s" % (module_name.__name__, func.__name__)
            insp_title, sep, insp_description = inspect.getdoc(func).partition("\n")
            self.__sources[uid] = {
                "title": title or insp_title.strip("\n."),
                "description": description or insp_description.lstrip("\n").replace("\n", " "),
                "default_template": template,
                "context": context
            }

    def get_source_choices(self):
        """Returns all registered plugget sources, as choices usable in a form.
        
        A choice is a tuple in the form (title, uid).
        """
        return [(k, s['title']) for k, s in self.sources.items()]

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
