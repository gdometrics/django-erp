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

# Inspired by http://stackoverflow.com/a/7469395/1063729

class _Singleton(type):
    """Singleton pattern.
    """
    def __init__(cls, name, bases, dicts):
        cls.instance = None

    def __call__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(_Singleton, cls).__call__(*args, **kwargs)
        return cls.instance

class LoggedInUserCache(object):
    """Stores the current user as a member attribute of a singleton.
    
    WARNING: if you manually change the value of "LoggedInUserCanche.user"
    property for your special purposes, remember to restore it ot its previous
    value at the end of your special code block. i.e.:

    >> logged_cache = LoggedInUserCache()
    >> current_user = logged_cache.current_user # Save the previous value!
    >> logged_cache.user = my_specific_needs_user
    >> # ... code ... #
    >> logged_cache.user = current_user # Restore the value!
    """
    __metaclass__ = _Singleton

    user = None

    def set_user(self, request):
        if request.user.is_authenticated():
            self.user = request.user

    @property
    def current_user(self):
        return self.user

    @property
    def has_user(self):
        return self.user is not None
