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

from cache import LoggedInUserCache
from backends import *
from management import *
from signals import *
from templatetags.permfuncs import *

user_model = get_user_model()
ob = ObjectPermissionBackend()
logged_cache = LoggedInUserCache()

def _clear_perm_caches(user):
    """Helper function which clears perms caches of the given user.
    """
    if hasattr(user, '_perm_cache'):
        delattr(user, '_perm_cache')
    if hasattr(user, '_group_perm_cache'):
        delattr(user, '_group_perm_cache')
    if hasattr(user, '_obj_perm_cache'):
        delattr(user, '_obj_perm_cache')
    if hasattr(user, '_group_obj_perm_cache'):
        delattr(user, '_group_obj_perm_cache')

class ObjectPermissionManagerTestCase(unittest.TestCase):
    def test_get_or_create_perm_by_natural_key(self):
        """Tests "ObjectPermissionManager.get(_or_create)_by_natural_key" method.
        """
        op, n = ObjectPermission.objects.get_or_create_by_natural_key("view_user", "auth", "user", 1)
        
        self.assertEqual(op.perm.content_type.app_label, "auth")
        self.assertEqual(op.perm.content_type.model, "user")
        self.assertEqual(op.perm.codename, "view_user")
        self.assertEqual(op.object_id, 1)
        
    def test_get_or_create_perm_by_uid(self):
        """Tests "ObjectPermissionManager.get(_or_create)_by_uid" method.
        """
        op, n = ObjectPermission.objects.get_or_create_by_uid("auth.view_user.1")
        
        self.assertEqual(op.perm.content_type.app_label, "auth")
        self.assertEqual(op.perm.content_type.model, "user")
        self.assertEqual(op.perm.codename, "view_user")
        self.assertEqual(op.object_id, 1)

class ObjectPermissionBackendTestCase(unittest.TestCase):
    def test_has_perm(self):
        """Tests simple object permissions between three different instances.
        """
        u, n = user_model.objects.get_or_create(username="u")
        u1, n = user_model.objects.get_or_create(username="u1")
        u2, n = user_model.objects.get_or_create(username="u2")
        p = Permission.objects.get_by_natural_key("delete_user", "auth", "user")
        
        self.assertFalse(ob.has_perm(u, p, u1))
        self.assertFalse(ob.has_perm(u, p, u2))
        
        u1.user_permissions.add(p)
        
        # Please keep in mind that ObjectPermissionBackend only takek in account
        # row/object-level permissions over a certain model instance, without
        # knowing anything about model-level permissions over its model class.
        self.assertFalse(ob.has_perm(u1, p, u))
        self.assertFalse(ob.has_perm(u1, p, u2))
        
        op, n = ObjectPermission.objects.get_or_create(object_id=u.pk, perm=p)
        op.users.add(u2)
        
        self.assertTrue(ob.has_perm(u2, p, u))
        self.assertFalse(ob.has_perm(u2, p, u1))
        
    def test_has_perm_by_name(self):
        """Tests retrieving object permissions by names.
        """
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
    def test_user_has_perms_on_itself(self):
        """Tests obj permissions to itself must be auto-added to user.
        """
        u1, n = user_model.objects.get_or_create(username="u1")
        
        self.assertTrue(ob.has_perm(u1, "auth.view_user", u1))
        self.assertTrue(ob.has_perm(u1, "auth.change_user", u1))
        self.assertTrue(ob.has_perm(u1, "auth.delete_user", u1))
        
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
        """Tests that "manage_author_permissions" auto-generate perms for author. 
        """
        u3, n = user_model.objects.get_or_create(username="u3", password="pwd")
        u4, n = user_model.objects.get_or_create(username="u4")
        
        self.assertFalse(ob.has_perm(u3, "auth.view_user", u4))
        self.assertFalse(ob.has_perm(u3, "auth.change_user", u4))
        self.assertFalse(ob.has_perm(u3, "auth.delete_user", u4))
        
        self.assertFalse(ob.has_perm(u4, "auth.view_user", u3))
        self.assertFalse(ob.has_perm(u4, "auth.change_user", u3))
        self.assertFalse(ob.has_perm(u4, "auth.delete_user", u3))
        
        manage_author_permissions(user_model)
        prev_user = logged_cache.current_user
        
        # The current author ("logged" user) is now u3.
        logged_cache.user = u3
        u5, n = user_model.objects.get_or_create(username="u5")
        u6, n = user_model.objects.get_or_create(username="u6")
        
        _clear_perm_caches(u3)
        
        self.assertTrue(ob.has_perm(u3, u"auth.view_user", u5))
        self.assertTrue(ob.has_perm(u3, u"auth.change_user", u5))
        self.assertTrue(ob.has_perm(u3, u"auth.delete_user", u5))
        
        self.assertFalse(ob.has_perm(u5, u"auth.view_user", u3))
        self.assertFalse(ob.has_perm(u5, u"auth.change_user", u3))
        self.assertFalse(ob.has_perm(u5, u"auth.delete_user", u3))
        
        # Restores previous cached user.
        logged_cache.user = prev_user
        
class TemplateTagsCase(unittest.TestCase):
    def test_user_has_perm(self):
        """Tests that "user_has_perm" check perms on both model and obj levels.
        """            
        u7, n = user_model.objects.get_or_create(username="u7")
        u8, n = user_model.objects.get_or_create(username="u8")
        
        prev_user = logged_cache.current_user
        
        # Checking perms for u7 (saved in LoggedInUserCache).
        logged_cache.user = u7
        self.assertFalse(user_has_perm(u8, u"auth.view_user"))
        self.assertFalse(user_has_perm(u8, u"auth.change_user"))
        self.assertFalse(user_has_perm(u8, u"auth.delete_user"))
        
        op, n = ObjectPermission.objects.get_or_create_by_uid("auth.view_user.%s" % u8.pk)
        u7.objectpermissions.add(op)
        
        _clear_perm_caches(u7)
    
        self.assertTrue(user_has_perm(u8, u"auth.view_user"))
        self.assertFalse(user_has_perm(u8, u"auth.change_user"))
        self.assertFalse(user_has_perm(u8, u"auth.delete_user"))
        
        p, n = Permission.objects.get_or_create_by_uid("auth.change_user")
        u7.user_permissions.add(p)
        
        _clear_perm_caches(u7)
        
        self.assertTrue(user_has_perm(u8, u"auth.view_user"))
        self.assertTrue(user_has_perm(u8, u"auth.change_user"))
        self.assertFalse(user_has_perm(u8, u"auth.delete_user"))
        
        # Restores previous cached user.
        logged_cache.user = prev_user
        
        
        
