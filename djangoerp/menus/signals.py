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

from django.conf import settings
from django.db.models.signals import post_save, pre_delete
from djangoerp.core.utils import get_model
from djangoerp.core.signals import manage_author_permissions

from models import Menu, Link, Bookmark
from utils import create_bookmarks, delete_bookmarks

## HANDLERS ##

def _create_bookmarks(sender, instance, *args, **kwargs):
    create_bookmarks(instance)

def _delete_bookmarks(sender, instance, *args, **kwargs):
    delete_bookmarks(instance)

## API ##

def manage_bookmarks(cls):
    """Connects handlers for bookmarks management.
    
    This handler could be used to automatically create a related bookmark list
    on given model class instance creation. i.e.:
    
    >> manage_bookmarks(User)
        
    It will auto generate a bookmark list associated to each new User's instance.
    """
    cls = get_model(cls)
    cls_name = cls.__name__.lower()
    post_save.connect(_create_bookmarks, cls, dispatch_uid="create_%s_bookmarks" % cls_name)
    pre_delete.connect(_delete_bookmarks, cls, dispatch_uid="delete_%s_bookmarks" % cls_name)

## CONNECTIONS ##

manage_author_permissions(Menu)
manage_author_permissions(Link)
manage_author_permissions(Bookmark)

manage_bookmarks(settings.AUTH_USER_MODEL)
