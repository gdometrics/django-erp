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

from django.test import TestCase
from djangoerp.authtools.backends import ObjectPermissionBackend
from djangoerp.authtools.cache import LoggedInUserCache

from models import Bookmark
from views import BookmarkCreateUpdateMixin
from utils import *
from signals import *

user_model = get_user_model()
ob = ObjectPermissionBackend()
logged_cache = LoggedInUserCache()

class _FakeRequest(object):
    def __init__(self):
        self.META = {'HTTP_HOST': "myhost.com", 'HTTP_REFERER': "http://myhost.com/bookmarks/"}
    
class _FakeBaseView(object):
    def get_initial(self):
        return {}
        
class _FakeBookmarkCreateUpdateView(BookmarkCreateUpdateMixin, _FakeBaseView):
    pass  
        
class UtilsTestCase(TestCase):
    def test_bookmarks_for_user(self):
        """Tests retrieving bookmark list owned by user with a given username.
        """        
        u1, n = user_model.objects.get_or_create(username="u1")
        
        self.assertTrue(n)
        
        bookmarks = Menu.objects.get(slug="user_1_bookmarks")
        
        self.assertEqual(get_bookmarks_for(u1.username), bookmarks)
        
    def test_user_of_bookmarks(self):
        """Tests retrieving the user of bookmarks identified by the given slug.
        """        
        u1, n = user_model.objects.get_or_create(username="u1")
        bookmarks = Menu.objects.get(slug="user_1_bookmarks")
        
        self.assertEqual(get_user_of(bookmarks.slug), u1) 

class MenuTestCase(TestCase):
    pass
    
class LinkTestCase(TestCase):
    pass

class BookmarkTestCase(TestCase):
    pass
    
class BookmarkCreateUpdateMixinTestCase(TestCase):
    def test_get_initial_url_on_creation(self):
        """Tests the initial URL is set on the current path on bookmark creation.
        """
        view = _FakeBookmarkCreateUpdateView()
        view.request = _FakeRequest()
        view.object = None
        self.assertEqual(view.get_initial(), {"url": "/bookmarks/"})
        
    def test_get_initial_url_on_editing(self):
        """Tests the initial URL is not set on bookmark editing.
        """
        view = _FakeBookmarkCreateUpdateView()
        view.request = _FakeRequest()
        view.object = Bookmark()
        self.assertEqual(view.get_initial(), {})
