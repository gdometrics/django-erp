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
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model

from . import *
from ..templatetags.modelfuncs import *
from ..templatetags.basefuncs import *
from ..templatetags.permfuncs import *
        
class JoinStringsTemplateTagTestCase(TestCase):
    def test_join_list_with_empty_string(self):
        """Tests "join" templatetag must exclude empty/invalid strings.
        """
        self.assertEqual(join("_", "a", "b", "", "d"), "a_b_d")
    
class ModelNameFilterTestCase(TestCase):
    def test_valid_model_name(self):
        """Tests returning of a valid model name using "model_name" filter.
        """
        self.assertEqual(model_name(get_user_model()), _("user")) 
        self.assertEqual(model_name(get_user_model()), _("user"))
        
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
        self.assertEqual(model_name_plural(get_user_model()), _("users")) 
        self.assertEqual(model_name_plural(get_user_model()), _("users"))
        
    def test_proxy_model_name(self):
        """Tests proxy-model name must be returned instead of concrete one.
        """
        class ProxyUser(get_user_model()):
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
        qs = get_user_model().objects.none()
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
        qs = get_user_model().objects.none()
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
        u1, n = get_user_model().objects.get_or_create(username="u1")
        qs = get_user_model().objects.filter(username=u1.username)
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
        u1, n = get_user_model().objects.get_or_create(username="u1")
        u2, n = get_user_model().objects.get_or_create(username="u2")
        u3, n = get_user_model().objects.get_or_create(username="u3")
        qs = get_user_model().objects.all()
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
        u1, n = get_user_model().objects.get_or_create(username="u1")
        u2, n = get_user_model().objects.get_or_create(username="u2")
        u3, n = get_user_model().objects.get_or_create(username="u3")
        
        qs = get_user_model().objects.order_by("-username")
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
        
        qs = get_user_model().objects.order_by("username")
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
        u1, n = get_user_model().objects.get_or_create(username="u1")
        u2, n = get_user_model().objects.get_or_create(username="u2")
        u3, n = get_user_model().objects.get_or_create(username="u3")
        
        qs = get_user_model().objects.filter(username__lt="u3")
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
        
class ModelDetailsTagTestCase(TestCase):
    def test_render_empty_model_details(self):
        """Tests rendering an empty model details table.
        """
        details_dict = {
            "uid": "",
            "num_cols": 0,
            "layout": []
        }
        
        self.assertEqual(
            render_model_details({}, ""),
            render_to_string("elements/model_details.html", {"details": details_dict})
        )
        
    def test_render_empty_model_details_with_uid(self):
        """Tests rendering an empty model details table with a custom UID.
        """
        details_dict = {
            "uid": "mydetails",
            "num_cols": 0,
            "layout": []
        }
        
        self.assertEqual(
            render_model_details({}, "", uid="mydetails"),
            render_to_string("elements/model_details.html", {"details": details_dict})
        )
        
    def test_render_one_object_model_details(self):
        """Tests rendering a model details table with one model instances.
        """
        u1, n = get_user_model().objects.get_or_create(username="u1")
        
        details_dict = {
            "uid": "",
            "num_cols": 1,
            "layout": [[{"name": "Username:", "attrs": "", "value": "u1"}]]
        }
        
        self.assertEqual(
            render_model_details({}, u1, ['username']),
            render_to_string("elements/model_details.html", {"details": details_dict})
        )
        
    def test_render_more_objects_model_details(self):
        """Tests rendering a model details table with multiple model instances.
        """
        u1, n = get_user_model().objects.get_or_create(username="u1")
        u2, n = get_user_model().objects.get_or_create(username="u2")
        
        details_dict = {
            "uid": "",
            "num_cols": 1,
            "layout": [
                [{"name": "Username:", "attrs": "", "value": "u1"}],
                [{"name": "Username:", "attrs": "", "value": "u2"}],
            ]
        }
        
        self.assertEqual(
            render_model_details({}, [u1, u2], ['0.username', '1.username']),
            render_to_string("elements/model_details.html", {"details": details_dict})
        )
        
    def test_render_multiple_column_model_details(self):
        """Tests rendering a model details table with more columns on one row.
        """
        u1, n = get_user_model().objects.get_or_create(username="u1")
        u2, n = get_user_model().objects.get_or_create(username="u2")
        
        details_dict = {
            "uid": "",
            "num_cols": 2,
            "layout": [
                [{"name": "Username:", "attrs": "", "value": "u1"}, {"name": "Username:", "attrs": "", "value": "u2"}],
            ]
        }
        
        self.assertEqual(
            render_model_details({}, [u1, u2], [['0.username', '1.username']]),
            render_to_string("elements/model_details.html", {"details": details_dict})
        )
        
    def test_render_model_details_with_suffixes(self):
        """Tests rendering a model details table which uses custom suffixes.
        """
        u1, n = get_user_model().objects.get_or_create(username="u1")
        u2, n = get_user_model().objects.get_or_create(username="u2")
        
        details_dict = {
            "uid": "",
            "num_cols": 1,
            "layout": [
                [{"name": "Username:", "attrs": "", "value": "u1 (user)"}],
                [{"name": "Username:", "attrs": "", "value": "u2 (another user)"}],
            ]
        }
        
        self.assertEqual(
            render_model_details({}, [u1, u2], ['0.username:(user)', '1.username:(another user)']),
            render_to_string("elements/model_details.html", {"details": details_dict})
        )
        
class UserHasPermTagTestCase(TestCase):
    def test_user_has_perm(self):
        """Tests that "user_has_perm" check perms on both model and obj levels.
        """            
        u7, n = get_user_model().objects.get_or_create(username="u7")
        u8, n = get_user_model().objects.get_or_create(username="u8")
        
        prev_user = logged_cache.user
        
        # Checking perms for u7 (saved in LoggedInUserCache).
        logged_cache.user = u7
        self.assertFalse(user_has_perm(u8, u"%s.view_user" % auth_app))
        self.assertFalse(user_has_perm(u8, u"%s.change_user" % auth_app))
        self.assertFalse(user_has_perm(u8, u"%s.delete_user" % auth_app))
        
        op, n = ObjectPermission.objects.get_or_create_by_uid("%s.view_user.%s" % (auth_app, u8.pk))
        u7.objectpermissions.add(op)
        
        clear_perm_caches(u7)
    
        self.assertTrue(user_has_perm(u8, u"%s.view_user" % auth_app))
        self.assertFalse(user_has_perm(u8, u"%s.change_user" % auth_app))
        self.assertFalse(user_has_perm(u8, u"%s.delete_user" % auth_app))
        
        p, n = Permission.objects.get_or_create_by_uid("%s.change_user" % auth_app)
        u7.user_permissions.add(p)
        
        clear_perm_caches(u7)
        
        self.assertTrue(user_has_perm(u8, u"%s.view_user" % auth_app))
        self.assertTrue(user_has_perm(u8, u"%s.change_user" % auth_app))
        self.assertFalse(user_has_perm(u8, u"%s.delete_user" % auth_app))
        
        # Restores previous cached user.
        logged_cache.user = prev_user
