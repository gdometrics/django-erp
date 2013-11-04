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
from django.contrib.contenttypes.models import ContentType
from djangoerp.core.backends import ObjectPermissionBackend
from djangoerp.core.cache import LoggedInUserCache

from loading import get_plugget_sources
from models import Region, Plugget
from utils import *
from signals import *

user_model = get_user_model()
ob = ObjectPermissionBackend()
logged_cache = LoggedInUserCache()

class SourceCacheLoadingTestCase(TestCase):
    def test_source_cache_auto_discovering(self):
        """Tests the auto-discovering of plugget sources.
        """
        self.assertTrue("djangoerp.pluggets.pluggets.text" in get_plugget_sources())  
        
class UtilsTestCase(TestCase):
    def test_dashboard_for_user(self):
        """Tests retrieving the dashboard owned by user with a given username.
        """        
        u1, n = user_model.objects.get_or_create(username="u1")
        
        self.assertTrue(n)
        
        dashboard = Region.objects.get(slug="user_1_dashboard")
        
        self.assertEqual(get_dashboard_for(u1.username), dashboard)
        
    def test_user_of_dashboard(self):
        """Tests retrieving the user of dashboard identified by the given slug.
        """        
        u1, n = user_model.objects.get_or_create(username="u1")
        dashboard = Region.objects.get(slug="user_1_dashboard")
        
        self.assertEqual(get_user_of(dashboard.slug), u1)   

class RegionTestCase(TestCase):
    def test_get_absolute_url_without_owner(self):
        """Tests the "get_absolute_url" method of a region without owner object.
        """
        r1, n = Region.objects.get_or_create(slug="r1")
        self.assertEqual(r1.get_absolute_url(), "/")
        
    def test_get_absolute_url_with_user_as_owner(self):
        """Tests the "get_absolute_url" method of a region with an owner object.
        """
        u1, n = user_model.objects.get_or_create(username="u1")
        ct = ContentType.objects.get_for_model(u1)
        r2, n = Region.objects.get_or_create(slug="r2", content_type=ct, object_id=u1.pk)
        self.assertNotEqual(r2.get_absolute_url(), u1.get_absolute_url())
        self.assertEqual(r2.get_absolute_url(), "/")
        
    def test_get_absolute_url_with_owner(self):
        """Tests the "get_absolute_url" method of a region with an owner object.
        """
        # TODO: use a custom model as owner of a region.
        pass

class PluggetTestCase(TestCase):
    def test_get_absolute_url(self):
        """Tests the "get_absolute_url" method of a plugget.
        """
        r1, n = Region.objects.get_or_create(slug="r1")
        p1, n = Plugget.objects.get_or_create(region=r1, title="p1", source="djangoerp.pluggets.base.dummy", template="pluggets/base_plugget.html")
        self.assertEqual(p1.get_absolute_url(), r1.get_absolute_url())
        
class SignalTestCase(TestCase):
    def test_dashboard_auto_creation_for_users(self):
        """Tests a dashboard must be auto-created for new users.
        """
        self.assertEqual(Region.objects.filter(slug="user_1_dashboard").count(), 0)
        
        u1, n = user_model.objects.get_or_create(username="u1")
        
        self.assertEqual(Region.objects.filter(slug="user_1_dashboard").count(), 1)
        
    def test_manage_author_permissions_on_dashboard(self):
        """Tests that "manage_author_permissions" auto-generate perms for author. 
        """        
        u1, n = user_model.objects.get_or_create(username="u1")
        dashboard = get_dashboard_for(u1.username)
        
        self.assertTrue(ob.has_perm(u1, u"pluggets.view_region", dashboard))
        self.assertTrue(ob.has_perm(u1, u"pluggets.change_region", dashboard))
        self.assertTrue(ob.has_perm(u1, u"pluggets.delete_region", dashboard))        
        
    def test_manage_author_permissions_on_plugget(self):
        """Tests that "manage_author_permissions" auto-generate perms for author. 
        """
        u2, n = user_model.objects.get_or_create(username="u2")
        u3, n = user_model.objects.get_or_create(username="u3")
        
        prev_user = logged_cache.current_user
        
        # The current author ("logged" user) is now u2.
        logged_cache.user = u2
        
        p1, n = Plugget.objects.get_or_create(region=get_dashboard_for(u2.username), title="p1", source="djangoerp.pluggets.base.dummy", template="pluggets/base_plugget.html")
        
        self.assertTrue(ob.has_perm(u2, u"pluggets.view_plugget", p1))
        self.assertTrue(ob.has_perm(u2, u"pluggets.change_plugget", p1))
        self.assertTrue(ob.has_perm(u2, u"pluggets.delete_plugget", p1))
        
        self.assertFalse(ob.has_perm(u3, u"pluggets.view_plugget", p1))
        self.assertFalse(ob.has_perm(u3, u"pluggets.change_plugget", p1))
        self.assertFalse(ob.has_perm(u3, u"pluggets.delete_plugget", p1))
        
        # Restores previous cached user.
        logged_cache.user = prev_user
