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
from django.contrib.auth.models import User

from models import *
from utils import *
from utils.dependencies import *
from utils.rendering import *
from templatetags.modelfuncs import *

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

class RenderingFieldToValueCase(TestCase):
    pass

class RenderingFieldToStringCase(TestCase):
    pass
    
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
        
        self.assertEqual(
        
            render_model_list(qs, ["username"]),
            
            render_to_string(
                "elements/model_list.html",
                {
                    "table": {
                        "uid": "",
                        "headers": [
                            {"name": "username", "type": "char"}
                        ],
                        "rows": [
                        ]
                    }
                }
            )
        )
        
    def test_render_one_row_model_list(self):
        """Tests rendering a model list table with one model instances.
        """
        u1, n = User.objects.get_or_create(username="u1")
        qs = User.objects.filter(username=u1.username)
        
        self.assertEqual(
        
            render_model_list(qs, ["username"]),
            
            render_to_string(
                "elements/model_list.html",
                {
                    "table": {
                        "uid": "",
                        "headers": [
                            {"name": "username", "type": "char"}
                        ],
                        "rows": [
                            {"object": qs[0], "fields": [qs[0].username]}
                        ]
                    }
                }
            )
        )
        
    def test_render_model_list(self):
        """Tests rendering a model list table with many model instances.
        """
        u1, n = User.objects.get_or_create(username="u1")
        u1, n = User.objects.get_or_create(username="u2")
        u1, n = User.objects.get_or_create(username="u3")
        qs = User.objects.all()
        
        self.assertEqual(
        
            render_model_list(qs, ["username"]),
            
            render_to_string(
                "elements/model_list.html",
                {
                    "table": {
                        "uid": "",
                        "headers": [
                            {"name": "username", "type": "char"}
                        ],
                        "rows": [
                            {"object": qs[0], "fields": [qs[0].username]},
                            {"object": qs[1], "fields": [qs[1].username]},
                            {"object": qs[2], "fields": [qs[2].username]}
                        ]
                    }
                }
            )
        )
