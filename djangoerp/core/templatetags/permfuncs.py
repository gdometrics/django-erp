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

from django import template
from django.contrib import auth

from ..cache import LoggedInUserCache

register = template.Library()

@register.filter
def user_has_perm(obj, perm_name):
    """Returns True if the user has permission "perm_name" over "obj".
    
    Looks for a suitable permission on both model and object-levels, iterating
    over all installed backends.

    Example usage: {{ article_object|user_has_perm:"articles.change_article" }}
    """
    current_user = LoggedInUserCache().user
    
    for backend in auth.get_backends():
        if hasattr(backend, "has_perm"):
            if backend.has_perm(current_user, perm_name):
                return True
            elif backend.has_perm(current_user, perm_name, obj):
                return True
                
    return False
