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
from django.forms import Form, ModelForm
from django.contrib.admin.helpers import AdminForm
from django.contrib.auth import get_user_model

from ..forms import *

class EnrichFormTestCase(TestCase):
    def test_enrich_form_class(self):
        """Tests that an enriched form class should have correct css classes.
        """
        class TestForm(Form):
            pass
            
        f = TestForm()
            
        self.assertFalse(hasattr(f, "required_css_class"))
        self.assertFalse(hasattr(f, "error_css_class"))
        
        enrich_form(TestForm)
        
        f = TestForm()
            
        self.assertTrue(hasattr(f, "required_css_class"))
        self.assertEqual(f.required_css_class, "required")
        self.assertTrue(hasattr(f, "error_css_class"))
        self.assertEqual(f.error_css_class, "errors")
        
    def test_enrich_form_instance(self):
        """Tests that an enriched form instance should have correct css classes.
        """
        class TestForm(Form):
            pass
            
        f = TestForm()
            
        self.assertFalse(hasattr(f, "required_css_class"))
        self.assertFalse(hasattr(f, "error_css_class"))
        
        enrich_form(f)
            
        self.assertTrue(hasattr(f, "required_css_class"))
        self.assertEqual(f.required_css_class, "required")
        self.assertTrue(hasattr(f, "error_css_class"))
        self.assertEqual(f.error_css_class, "errors")
        
    def test_enrich_model_form_instance(self):
        """Tests the correct enrichment of a model form instance too.
        """
        class TestModelForm(ModelForm):
            class Meta:
                model = get_user_model()
            
        f = TestModelForm()
            
        self.assertFalse(hasattr(f, "required_css_class"))
        self.assertFalse(hasattr(f, "error_css_class"))
        
        enrich_form(f)
            
        self.assertTrue(hasattr(f, "required_css_class"))
        self.assertEqual(f.required_css_class, "required")
        self.assertTrue(hasattr(f, "error_css_class"))
        self.assertEqual(f.error_css_class, "errors")
