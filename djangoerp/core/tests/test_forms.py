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
from django.forms import Form, ModelForm, ValidationError
from django.utils.encoding import force_text
from django.contrib.admin.helpers import AdminForm
from django.contrib.auth import get_user_model

from ..forms import *
from ..forms.auth import *

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
        
class UserFormTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(username="u1", email="u@u.it")
        self.user_data = {'username': 'u1', 'email': 'u@u.it', 'timezone': 'GMT', 'language': 'en'}
        
    def test_raise_exception_when_no_password1_on_creation(self):
        """Tests raising an error when no password is provided on user creation.
        """
        f = UserForm()
        
        self.assertTrue(f.fields['password1'].required)
        self.assertTrue(f.fields['password2'].required)
        self.assertFalse(f.is_valid())
        
    def test_no_password_required_on_editing(self):
        """Tests no password is required on user editing.
        """
        f = UserForm(self.user_data, instance=self.user)
        
        self.assertFalse(f.fields['password1'].required)
        self.assertFalse(f.fields['password2'].required)
        self.assertTrue(f.is_valid())
        
    def test_clean_password1(self):
        """Tests cleaning password's value.
        """
        f = UserForm({"password1": "password"}, instance=self.user)
        
        f.is_valid()
              
        self.assertEqual(f.cleaned_data['password1'], "password")
        
    def test_clean_password2(self):
        """Tests cleaning password's value.
        """
        test_data = self.user_data
        test_data.update({"password1": "password", "password2": "password"})
        
        f = UserForm(test_data, instance=self.user)
        
        self.assertTrue(f.is_valid())
        
    def test_error_when_passwords_are_not_equal(self):
        """Tests an error must be raised if password values are not equal.
        """
        test_data = self.user_data
        test_data.update({"password1": "password", "password2": "password2"})
        
        f = UserForm(test_data, instance=self.user)
        
        self.assertFalse(f.is_valid())
        
