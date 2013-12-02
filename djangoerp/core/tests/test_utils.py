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
from ..utils import *
from ..utils.dependencies import *
from ..utils.rendering import *
          
class GetModelTestCase(TestCase):
    def test_invalid_klass(self):
        """Tests "get_model" func must raise a ValueError.
        """
        try:
            m = get_model(None)
            self.assertFalse(True)
        except ValueError:
            self.assertTrue(True)
            
    def test_model_klass(self):
        """Tests "get_model" func when a real model class is passed.
        """
        try:
            m = get_model(get_user_model())
            self.assertEqual(m, get_user_model())
        except ValueError:
            self.assertFalse(True)
            
    def test_model_instance(self):
        """Tests "get_model" func when a real model instance is passed.
        """
        try:
            u, n = get_user_model().objects.get_or_create(username="user_instance")
            m = get_model(u)
            self.assertEqual(m, get_user_model())
        except ValueError:
            self.assertFalse(True)
            
    def test_model_queryset(self):
        """Tests "get_model" func when a real model queryset is passed.
        """
        try:
            qs = get_user_model().objects.all()
            m = get_model(qs)
            self.assertEqual(m, get_user_model())
        except ValueError:
            self.assertFalse(True)
            
    def test_model_string(self):
        """Tests "get_model" func when a model string is passed.
        """
        try:
            m = get_model(user_model_string)
            self.assertEqual(m, get_user_model())
        except ValueError:
            self.assertFalse(True)
          
class CleanHTTPRefererCase(TestCase):            
    def test_no_request(self):
        """Tests when there isn't a request, default_referer must be returned.
        """
        default_referer = '/'
        self.assertEqual(clean_http_referer(None, default_referer), default_referer)
            
    def test_other_site_referer(self):
        """Tests that a valid referer is correctly returned by the function.
        """
        request = FakeRequest()
        self.assertEqual(clean_http_referer(request), "www.test.com")
            
    def test_host_strip_referer(self):
        """Tests the current host should be stripped out.
        """
        expected_referer = '/test'
        request = FakeRequest()
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
