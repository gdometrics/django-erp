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
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from cache import LoggedInUserCache
from backends import *
from management import *
from signals import *
from models import *
from utils import *
from utils.dependencies import *
from utils.rendering import *
from templatetags.modelfuncs import *
from templatetags.basefuncs import *
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

class _FakeRequest(object):
    def __init__(self):
        self.META = {'HTTP_HOST': "myhost.com", 'HTTP_REFERER': "http://www.test.com"}

class JSONValidationCase(TestCase):
    def test_correct_json_validation(self):
        """Tests that when a JSON snippet is incorrect, an error must be raised.
        """
        try:
          validate_json('{"id":1,"name":"foo","interest":["django","django ERP"]}')
          self.assertTrue(True)
        except ValidationError:
          self.assertFalse(True)
          
    def test_incorrect_json_validation(self):
        """Tests that when a JSON snippet is incorrect, an error must be raised.
        """
        try:
          # The snippet is incorrect due to the double closed square bracket.
          validate_json('{"id":1,"name":"foo","interest":["django","django ERP"]]}')
          self.assertFalse(True)
        except ValidationError:
          self.assertTrue(True)
          
class CleanHTTPRefererCase(TestCase):            
    def test_no_request(self):
        """Tests when there isn't a request, default_referer must be returned.
        """
        default_referer = '/'
        self.assertEqual(clean_http_referer(None, default_referer), default_referer)
            
    def test_other_site_referer(self):
        """Tests that a valid referer is correctly returned by the function.
        """
        request = _FakeRequest()
        self.assertEqual(clean_http_referer(request), "www.test.com")
            
    def test_host_strip_referer(self):
        """Tests the current host should be stripped out.
        """
        expected_referer = '/test'
        request = _FakeRequest()
        request.META["HTTP_REFERER"] = request.META['HTTP_HOST'] + expected_referer
        self.assertEqual(clean_http_referer(request), expected_referer)  

class DependencyCase(TestCase):
    def test_satisfied_dependency(self):
        """Tests that when a dependency is satisfied, no error is raised.
        """
        try:
          check_dependency("djangoerp.core")
          self.assertTrue(True)
        except DependencyError:
          self.assertTrue(False)

    def test_not_satisfied_dependency(self):
        """Tests that when a dependency is not satisfied, an error must be raised.
        """
        try:
          check_dependency("supercalifragidilistichespiralidoso.core")
          self.assertTrue(False)
        except DependencyError:
          self.assertTrue(True)

class RenderingValueToStringCase(TestCase):
    def test_empty_value_to_string(self):
        """Tests rendering of an empty value.
        """
        self.assertEqual(value_to_string(None), mark_safe(render_to_string('elements/empty.html', {})))

    def test_bool_true_value_to_string(self):
        """Tests rendering of a valid boolean value.
        """
        self.assertEqual(value_to_string(True), mark_safe(render_to_string('elements/yes.html', {})))

    def test_bool_true_value_to_string(self):
        """Tests rendering of an invalid boolean value.
        """
        self.assertEqual(value_to_string(False), mark_safe(render_to_string('elements/no.html', {})))

    def test_float_value_to_string(self):
        """Tests rendering of a float value.
        """
        self.assertEqual(value_to_string(2.346), '2.35')

    def test_integer_value_to_string(self):
        """Tests rendering of an integer value.
        """
        self.assertEqual(value_to_string(2346), '2346')

    def test_list_value_to_string(self):
        """Tests rendering of a list.
        """
        self.assertEqual(value_to_string([None, True]), '%s, %s' % (mark_safe(render_to_string('elements/empty.html', {})), mark_safe(render_to_string('elements/yes.html', {}))))

    def test_tuple_value_to_string(self):
        """Tests rendering of a list.
        """
        self.assertEqual(value_to_string((None, False)), '%s, %s' % (mark_safe(render_to_string('elements/empty.html', {})), mark_safe(render_to_string('elements/no.html', {}))))
        
class JoinStringsTemplateTagTestCase(TestCase):
    def test_join_list_with_empty_string(self):
        """Tests "join" templatetag must exclude empty/invalid strings.
        """
        self.assertEqual(join("_", "a", "b", "", "d"), "a_b_d")
    
class ModelNameFilterTestCase(TestCase):
    def test_valid_model_name(self):
        """Tests returning of a valid model name using "model_name" filter.
        """
        self.assertEqual(model_name(User), _("user")) 
        self.assertEqual(model_name(User()), _("user"))
        
    def test_invalid_model_name(self):
        """Tests "model_name" filter on an invalid input.
        """
        class FakeObject:
            pass
            
        self.assertEqual(model_name(FakeObject), "") 
        self.assertEqual(model_name(FakeObject()), "")
        
    def test_plural_model_name(self):
        """Tests returning of a plural model name using "model_name" filter.
        """
        self.assertEqual(model_name_plural(User), _("users")) 
        self.assertEqual(model_name_plural(User()), _("users"))
        
    def test_proxy_model_name(self):
        """Tests proxy-model name must be returned instead of concrete one.
        """
        class ProxyUser(User):
            class Meta:
                proxy = True
                verbose_name = _('proxy user')
                verbose_name_plural = _('proxy users')
                
        self.assertEqual(model_name(ProxyUser), _('proxy user'))
        self.assertEqual(model_name(ProxyUser()), _('proxy user'))
        self.assertEqual(model_name_plural(ProxyUser), _('proxy users'))
        self.assertEqual(model_name_plural(ProxyUser()), _('proxy users'))
        
class ModelListTagTestCase(TestCase):
    def test_render_empty_model_list(self):
        """Tests rendering an empty model list table.
        """
        qs = User.objects.none()
        table_dict = {
            "uid": "",
            "order_by": [],
            "headers": [
                {"name": "username", "attname": "username", "type": "char", "filter": {"expr": "", "value": ""}}
            ],
            "rows": [
            ]
        }
        
        self.assertEqual(
            render_model_list({}, qs, ["username"]),
            render_to_string("elements/model_list.html", {"table": table_dict})
        )
        
    def test_render_empty_model_list_with_uid(self):
        """Tests rendering an empty model list table with a custom UID.
        """
        qs = User.objects.none()
        table_dict = {
            "uid": "mytable",
            "order_by": [],
            "headers": [
                {"name": "username", "attname": "username", "type": "char", "filter": {"expr": "", "value": ""}}
            ],
            "rows": [
            ]
        }
        
        self.assertEqual(
            render_model_list({}, qs, ["username"], uid="mytable"),
            render_to_string("elements/model_list.html", {"table": table_dict})
        )
        
    def test_render_one_row_model_list(self):
        """Tests rendering a model list table with one model instances.
        """
        u1, n = User.objects.get_or_create(username="u1")
        qs = User.objects.filter(username=u1.username)
        table_dict = {
            "uid": "",
            "order_by": [],
            "headers": [
                {"name": "username", "attname": "username", "type": "char", "filter": {"expr": "", "value": ""}}
            ],
            "rows": [
                {"object": u1, "fields": [u1.username]}
            ]
        }
        
        self.assertEqual(
            render_model_list({}, qs, ["username"]),
            render_to_string("elements/model_list.html", {"table": table_dict})
        )
        
    def test_render_model_list(self):
        """Tests rendering a model list table with many model instances.
        """
        u1, n = User.objects.get_or_create(username="u1")
        u2, n = User.objects.get_or_create(username="u2")
        u3, n = User.objects.get_or_create(username="u3")
        qs = User.objects.all()
        table_dict = {
            "uid": "",
            "order_by": [],
            "headers": [
                {"name": "username", "attname": "username", "type": "char", "filter": {"expr": "", "value": ""}}
            ],
            "rows": [
                {"object": u1, "fields": [u1.username]},
                {"object": u2, "fields": [u2.username]},
                {"object": u3, "fields": [u3.username]}
            ]
        }
        
        self.assertEqual(
            render_model_list({}, qs, ["username"]),
            render_to_string("elements/model_list.html", {"table": table_dict})
        )
        
    def test_render_ordered_model_list(self):
        """Tests rendering a model list table with an ordered queryset.
        """
        u1, n = User.objects.get_or_create(username="u1")
        u2, n = User.objects.get_or_create(username="u2")
        u3, n = User.objects.get_or_create(username="u3")
        
        qs = User.objects.order_by("-username")
        table_dict = {
            "uid": "",
            "order_by": [],
            "headers": [
                {"name": "username", "attname": "username", "type": "char", "filter": {"expr": "", "value": ""}}
            ],
            "rows": [
                {"object": u3, "fields": [u3.username]},
                {"object": u2, "fields": [u2.username]},
                {"object": u1, "fields": [u1.username]}
            ]
        }
        
        self.assertEqual(
            render_model_list({}, qs, ["username"]),
            render_to_string("elements/model_list.html", {"table": table_dict})
        )
        
        qs = User.objects.order_by("username")
        table_dict.update({
            "order_by": ["username"],
            "rows": [
                {"object": u1, "fields": [u1.username]},
                {"object": u2, "fields": [u2.username]},
                {"object": u3, "fields": [u3.username]}
            ]
        })
        
        self.assertEqual(
            render_model_list({}, qs, ["username"]),
            render_to_string("elements/model_list.html", {"table": table_dict})
        )
        
    def test_render_filtered_model_list(self):
        """Tests rendering a model list table with a filtered queryset.
        """
        u1, n = User.objects.get_or_create(username="u1")
        u2, n = User.objects.get_or_create(username="u2")
        u3, n = User.objects.get_or_create(username="u3")
        
        qs = User.objects.filter(username__lt="u3")
        table_dict = {
            "uid": "",
            "order_by": [],
            "headers": [
                {"name": "username", "attname": "username", "type": "char", "filter": {"expr": "lt", "value": "u3"}}
            ],
            "rows": [
                {"object": u1, "fields": [u1.username]},
                {"object": u2, "fields": [u2.username]},
            ]
        }
        
        self.assertEqual(
            render_model_list({"list_filter_by": {"username": ("lt", "u3")}}, qs, ["username"]),
            render_to_string("elements/model_list.html", {"table": table_dict})
        )

class ObjectPermissionManagerTestCase(TestCase):
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

class ObjectPermissionBackendTestCase(TestCase):
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

class ManagementTestCase(TestCase):
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
        
    def test_assign_new_users_to_users_group(self):
        """Tests each new user must be assigned to "users" group.
        
        This is valid only if users are created NOT by the admin interface
        (i.e. registration).
        """
        u2, n = user_model.objects.get_or_create(username="u2")
        self.assertTrue(n)
        self.assertTrue(u2.groups.get(name="users"))        
        
class SignalTestCase(TestCase):
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
        
    def test_author_is_only_the_very_first_one(self):
        """Tests that perms must be auto-generated only for the first author. 
        """
        u3, n = user_model.objects.get_or_create(username="u3")
        u4, n = user_model.objects.get_or_create(username="u4")
        
        manage_author_permissions(user_model)
        prev_user = logged_cache.current_user
        
        # The current author ("logged" user) is now u3.
        logged_cache.user = u3
        u7, n = user_model.objects.get_or_create(username="u7")
        
        _clear_perm_caches(u3)
        
        self.assertTrue(ob.has_perm(u3, u"auth.view_user", u7))
        self.assertTrue(ob.has_perm(u3, u"auth.change_user", u7))
        self.assertTrue(ob.has_perm(u3, u"auth.delete_user", u7))
        
        self.assertFalse(ob.has_perm(u4, u"auth.view_user", u7))
        self.assertFalse(ob.has_perm(u4, u"auth.change_user", u7))
        self.assertFalse(ob.has_perm(u4, u"auth.delete_user", u7))
        
        # The current author ("logged" user) is now u4.
        logged_cache.user = u4
        
        u7.username = "u7_edited"
        u7.save()
        
        _clear_perm_caches(u4)
        
        self.assertFalse(ob.has_perm(u4, u"auth.view_user", u7))
        self.assertFalse(ob.has_perm(u4, u"auth.change_user", u7))
        self.assertFalse(ob.has_perm(u4, u"auth.delete_user", u7))
        
        # Restores previous cached user.
        logged_cache.user = prev_user
        
class TemplateTagsCase(TestCase):
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
