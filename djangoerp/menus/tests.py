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

from django.test import TestCase
from django.contrib.auth import get_user_model
from djangoerp.core.backends import ObjectPermissionBackend
from djangoerp.core.cache import LoggedInUserCache

from models import Bookmark
from views import BookmarkCreateUpdateMixin
from utils import *
from signals import *

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
        u1, n = get_user_model().objects.get_or_create(username="u1")
        
        self.assertTrue(n)
        
        bookmarks = Menu.objects.get(slug="user_1_bookmarks")
        
        self.assertEqual(get_bookmarks_for(u1.username), bookmarks)
        
    def test_user_of_bookmarks(self):
        """Tests retrieving the user of bookmarks identified by the given slug.
        """        
        u1, n = get_user_model().objects.get_or_create(username="u1")
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
        
class SignalTestCase(TestCase):
    def test_bookmarks_auto_creation_for_users(self):
        """Tests a bookmarks list must be auto-created for new users.
        """
        self.assertEqual(Menu.objects.filter(slug="user_1_bookmarks").count(), 0)
        
        u1, n = get_user_model().objects.get_or_create(username="u1")
        
        self.assertEqual(Menu.objects.filter(slug="user_1_bookmarks").count(), 1)
        
    def test_manage_author_permissions_on_bookmarks(self):
        """Tests that "manage_author_permissions" auto-generate perms for author. 
        """        
        u1, n = get_user_model().objects.get_or_create(username="u1")
        bookmarks = get_bookmarks_for(u1.username)
        
        self.assertTrue(ob.has_perm(u1, u"menus.view_menu", bookmarks))
        self.assertTrue(ob.has_perm(u1, u"menus.change_menu", bookmarks))
        self.assertTrue(ob.has_perm(u1, u"menus.delete_menu", bookmarks))        
        
    def test_manage_author_permissions_on_bookmark(self):
        """Tests that "manage_author_permissions" auto-generate perms for author. 
        """
        u2, n = get_user_model().objects.get_or_create(username="u2")
        u3, n = get_user_model().objects.get_or_create(username="u3")
        
        prev_user = logged_cache.current_user
        
        # The current author ("logged" user) is now u2.
        logged_cache.user = u2
        
        b1, n = Bookmark.objects.get_or_create(menu=get_bookmarks_for(u2.username), title="b1", url="/")
        
        self.assertTrue(ob.has_perm(u2, u"menus.view_link", b1))
        self.assertTrue(ob.has_perm(u2, u"menus.change_link", b1))
        self.assertTrue(ob.has_perm(u2, u"menus.delete_link", b1))
        
        self.assertFalse(ob.has_perm(u3, u"menus.view_link", b1))
        self.assertFalse(ob.has_perm(u3, u"menus.change_link", b1))
        self.assertFalse(ob.has_perm(u3, u"menus.delete_link", b1))
        
        # Restores previous cached user.
        logged_cache.user = prev_user
        
    def test_bookmarks_auto_deletion(self):
        """Tests automatic deletion of bookmarks when their owners are deleted.
        """
        d = None
        
        try:
            d = get_bookmarks_for("u4")
        except:
            pass
            
        self.assertEqual(d, None)
            
        u4, n = get_user_model().objects.get_or_create(username="u4")
        
        try:
            d = get_bookmarks_for("u4")
        except:
            pass
            
        self.assertNotEqual(d, None)
        
        u4.delete()
        
        try:
            d = get_bookmarks_for("u4")
        except:
            d = None
            
        self.assertEqual(d, None)
