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

from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from ..models import User
        
class AdminUserCreationForm(UserCreationForm):
    """A form that creates a user with no privileges.
    """
    class Meta:
        # This is the custom User model, not the Django's one.
        model = User

    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        username = self.cleaned_data["username"]
        try:
            # This is the custom User model, not the Django's one.
            User._default_manager.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(
            self.error_messages['duplicate_username'],
            code='duplicate_username',
        )

class AdminUserChangeForm(UserChangeForm):
    """A form for updating users.
    
    Includes all the fields on the user, but replaces the password field with
    admin's password hash display field.
    """
    class Meta:
        # This is the custom User model, not the Django's one.
        model = User

class RichForm(object):
    """Mix-in to make rich forms.
    """
    required_css_class = 'required'
    error_css_class = 'errors'

def enrich_form(cls):
    """Makes the form richer with custom CSS classes for special fields.
    """
    if RichForm not in cls.__bases__:
        cls.__bases__ += (RichForm,)
