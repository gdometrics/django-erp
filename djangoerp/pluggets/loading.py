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

from django.conf import settings

class _PluggetCache(object):
    def __init__(self):
        self.__sources = {}
        self.__discovered = False
        
    def register(self, func, title, description, template, form):
        if callable(func):
            import inspect
            module_name = inspect.getmodule(func)
            uid = "%s.%s" % (module_name.__name__, func.__name__)
            insp_title, sep, insp_description = inspect.getdoc(func).partition("\n")
            self.__sources[uid] = {
                "title": title or insp_title.strip("\n.") or func.__name__.capitalize(),
                "description": description or insp_description.lstrip("\n").replace("\n", " "),
                "default_template": template,
                "form": form
            }

    def get_source_choices(self):
        return [(k, s['title']) for k, s in self.sources.items()]

    def __get_sources(self):
        self.__auto_discover()
        return self.__sources
    sources = property(__get_sources)
    
    def __auto_discover(self):
        """ Auto discover pluggets of installed applications.
        """
        if self.__discovered:
            return
            
        for app in settings.INSTALLED_APPS:
            # Skip Django's apps.
            if app.startswith('django.'):
                continue
                
            # Try to import pluggets from the current app.
            module_name = "%s.pluggets" % app
            try:
                module = __import__(module_name, {}, {}, ['*'])
            except ImportError:
                pass
                
        self.__discovered = True

_plugget_registry = _PluggetCache()

## API ##

def register_plugget(func, title=None, description=None, template="pluggets/base_plugget.html", form=None):
    """Register a new plugget source.
    
    A plugget source is identified by:
    
     * func -- A callable which takes a context, manupulates and returns it.
     * title -- A default title for the plugget [optional].
                (default: title specified in func's docstring or its name)
     * description -- A description of purpose of the plugget [optional].
                      (default: the remaining part of func's docstring)
     * template -- Path of template that must be used to render the plugget.
     * form -- The form to be used for plugget customization.
    
    """
    _plugget_registry.register(func, title, description, template, form)
    
def get_plugget_sources():
    """Returns the list of all registered plugget sources.
    """
    return _plugget_registry.sources
    
def get_plugget_source(source_uid):
    """Returns the registered plugget sources identified by "source_uid".
    
    If the source is not registered, None is returned.
    """
    return _plugget_registry.sources.get(source_uid, None)
    
def get_plugget_source_choices():
    """Returns all registered plugget sources as a choice list for forms.
    
    A choice is a tuple in the form (source_title, source_uid).
    """
    return _plugget_registry.get_source_choices()
