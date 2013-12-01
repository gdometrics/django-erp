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
    
class ManagementInstallTestCase(TestCase):
    def test_install(self):
        """Tests app installation.
        """
        from djangoerp.core.models import Group, Permission
        from management import install
        
        install(None)
        
        # Menus.
        main_menu, is_new = Menu.objects.get_or_create(slug="main")
        self.assertTrue(main_menu)
        self.assertFalse(is_new)
    
        user_area_not_logged_menu, is_new = Menu.objects.get_or_create(slug="user_area_not_logged")
        self.assertTrue(user_area_not_logged_menu)
        self.assertFalse(is_new)
    
        user_area_logged_menu, is_new = Menu.objects.get_or_create(slug="user_area_logged")
        self.assertTrue(user_area_logged_menu)
        self.assertFalse(is_new)
    
        user_detail_actions, is_new = create_detail_actions(get_user_model())
        self.assertTrue(user_detail_actions)
        self.assertFalse(is_new)
    
        user_detail_navigation, is_new = create_detail_navigation(get_user_model())
        self.assertTrue(user_detail_navigation)
        self.assertFalse(is_new)
        
        # Links.
        my_dashboard_link, is_new = Link.objects.get_or_create(slug="my-dashboard")
        self.assertTrue(my_dashboard_link)
        self.assertFalse(is_new)
        
        login_link, is_new = Link.objects.get_or_create(slug="login")
        self.assertTrue(login_link)
        self.assertFalse(is_new)
        
        administration_link, is_new = Link.objects.get_or_create(slug="administration")
        self.assertTrue(administration_link)
        self.assertFalse(is_new)
        
        logout_link, is_new = Link.objects.get_or_create(slug="logout")
        self.assertTrue(logout_link)
        self.assertFalse(is_new)
        
        user_edit_link, is_new = Link.objects.get_or_create(slug="user-edit")
        self.assertTrue(user_edit_link)
        self.assertFalse(is_new)
        
        user_delete_link, is_new = Link.objects.get_or_create(slug="user-delete")
        self.assertTrue(user_delete_link)
        self.assertFalse(is_new)
        
        # Perms.
        users_group, is_new = Group.objects.get_or_create(name="users")
        
        self.assertTrue(user_edit_link.only_with_perms.get_by_natural_key("change_user", "core", "user"))
        self.assertTrue(users_group.permissions.get_by_natural_key("add_link", "menus", "link"))
        
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
