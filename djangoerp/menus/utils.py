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

from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

def get_bookmarks_for(username):
    """Returns the bookmarks menu for the user with the given username.
    """
    from models import Menu
    user = get_object_or_404(get_user_model(), username=username)
    return get_object_or_404(Menu, slug="user_%s_bookmarks" % user.pk)
    
def get_user_of(bookmarks_menu_slug):
    """Returns the owner of the given bookmarks list.
    """
    user_pk = bookmarks_menu_slug.split('_')[1]
    return get_object_or_404(get_user_model(), pk=user_pk)
