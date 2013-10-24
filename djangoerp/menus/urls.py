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

from views import *

urlpatterns = patterns('',

    url(r'^users/(?P<username>[\w\d\@\.\+\-\_]+)/bookmarks/$', view=ListBookmarkView.as_view(), name='bookmark_list'),
    url(r'^users/(?P<username>[\w\d\@\.\+\-\_]+)/bookmarks/add/$', view=CreateBookmarkView.as_view(), name='bookmark_add'),
    url(r'^users/(?P<username>[\w\d\@\.\+\-\_]+)/bookmarks/(?P<slug>[-\w]+)/edit/$', view=UpdateBookmarkView.as_view(), name='bookmark_edit'),
    url(r'^users/(?P<username>[\w\d\@\.\+\-\_]+)/bookmarks/(?P<slug>[-\w]+)/delete/$', view=DeleteBookmarkView.as_view(), name='bookmark_delete'),
)
