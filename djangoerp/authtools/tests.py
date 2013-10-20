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

from django.utils import unittest
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from backends import *
from management import *
from signals import *

class ObjectPermissionBackendTestCase(unittest.TestCase):
    def test_has_perm(self):
        """Tests simple object permissions between three different instances.
        """
        ob = ObjectPermissionBackend()
        user_model = get_user_model()
        
        u, n = user_model.objects.get_or_create(username="u")
        u1, n = user_model.objects.get_or_create(username="u1")
        u2, n = user_model.objects.get_or_create(username="u2")
        p = Permission.objects.get_by_natural_key("delete_user", "auth", "user")
        
        self.assertFalse(ob.has_perm(u, p, u1))
        self.assertFalse(ob.has_perm(u, p, u2))
        
        u1.user_permissions.add(p)
        
        self.assertTrue(ob.has_perm(u1, p, u))
        self.assertTrue(ob.has_perm(u1, p, u2))
        
        op, n = ObjectPermission.objects.get_or_create(object_id=u.pk, perm=p)
        op.users.add(u2)
        
        self.assertTrue(ob.has_perm(u2, p, u))
        self.assertFalse(ob.has_perm(u2, p, u1))
        
    def test_has_perm_by_name(self):
        """Tests retrieving object permissions by names.
        """
        ob = ObjectPermissionBackend()
        user_model = get_user_model()
        p_name = "auth.delete_user"
        
        u, n = user_model.objects.get_or_create(username="u")
        u1, n = user_model.objects.get_or_create(username="u1")
        u2, n = user_model.objects.get_or_create(username="u2")
        
        p = Permission.objects.get_by_natural_key("delete_user", "auth", "user")
        op, n = ObjectPermission.objects.get_or_create(object_id=u.pk, perm=p)
        op.users.add(u2)
        
        self.assertTrue(ob.has_perm(u2, p_name, u))
        self.assertFalse(ob.has_perm(u2, p_name, u1))

class ManagementTestCase(unittest.TestCase):
    def test_user_has_view_perm_on_itself(self):
        """Tests an obj permission to delete itself must be auto-added to user.
        """
        b = ObjectPermissionBackend()
        user_model = get_user_model()
        u1, n = user_model.objects.get_or_create(username="u1")
        
        self.assertTrue(b.has_perm(u1, "auth.view_user", u1))
        
    def test_create_contenttype_view_permission(self):
        """Tests a view permission must be auto-created on new contenttypes. 
        """
        model_name = "dog"
        codename = "view_%s" % model_name
        
        self.assertEqual(ContentType.objects.filter(model=model_name).count(), 0)
        self.assertEqual(Permission.objects.filter(codename=codename).count(), 0)
        
        ContentType.objects.get_or_create(model=model_name, app_label=model_name, name=model_name.capitalize())
        
        self.assertEqual(Permission.objects.filter(codename=codename).count(), 1)
        
class SignalTestCase(unittest.TestCase):
    def test_manage_author_permissions(self):
        """Tests manage_author_permissions auto-generates perms for author. 
        """
        from django.contrib.auth import authenticate
        from cache import LoggedInUserCache
            
        user_model = get_user_model()
        ob = ObjectPermissionBackend()
        u3, n = user_model.objects.get_or_create(username="u3", password="pwd")
        u4, n = user_model.objects.get_or_create(username="u4")
        
        self.assertFalse(ob.has_perm(u3, "auth.view_user", u4))
        self.assertFalse(ob.has_perm(u3, "auth.change_user", u4))
        self.assertFalse(ob.has_perm(u3, "auth.delete_user", u4))
        
        self.assertFalse(ob.has_perm(u4, "auth.view_user", u3))
        self.assertFalse(ob.has_perm(u4, "auth.change_user", u3))
        self.assertFalse(ob.has_perm(u4, "auth.delete_user", u3))
        
        manage_author_permissions(user_model)
        logged_cache = LoggedInUserCache()
        logged_cache.user = u3
        u5, n = user_model.objects.get_or_create(username="u5")
        u6, n = user_model.objects.get_or_create(username="u6")
        
        self.assertTrue(ob.has_perm(u3, u"auth.view_user", u5))
        self.assertTrue(ob.has_perm(u3, u"auth.change_user", u5))
        self.assertTrue(ob.has_perm(u3, u"auth.delete_user", u5))
        
        self.assertFalse(ob.has_perm(u5, u"auth.view_user", u3))
        self.assertFalse(ob.has_perm(u5, u"auth.change_user", u3))
        self.assertFalse(ob.has_perm(u5, u"auth.delete_user", u3))
        
        
        
