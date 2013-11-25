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

from django import forms
from django.utils.translation import ugettext_lazy as _
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

class UserForm(forms.ModelForm):
    """Form for user data.
    """
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'language', 'timezone']
        
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['password1'].required = (self.instance.pk is None)
        self.fields['password2'].required = (self.instance.pk is None)

    def clean_password1(self):
        """Checks for a valid password1.
        """
        password1 = self.cleaned_data["password1"]
            
        if not (password1 or self.instance.pk):
            raise forms.ValidationError(_('This field is required.'))
            
        return password1

    def clean_password2(self):
        """Checks if password2 is equal to password1.
        """
        password1 = self.cleaned_data.get("password1", None)
        password2 = self.cleaned_data["password2"]
        
        if password1 != password2 and (password2 or not self.instance.pk):
            raise forms.ValidationError(_("The two password fields didn't match."))
            
        if not (password2 or self.instance.pk):
            raise forms.ValidationError(_('This field is required.'))
            
        return password2

    def save(self, commit=True):
        user = super(UserForm, self).save(commit=False)
        if self.cleaned_data['password1'] or not user.password:
            user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            self.save_m2m()   
        return user

class RichForm(object):
    """Mix-in to make rich forms.
    """
    required_css_class = "required"
    error_css_class = "errors"

def enrich_form(cls):
    """Makes the form richer with custom CSS classes for special fields.
    """
    if RichForm not in cls.__bases__:
        cls.__bases__ += (RichForm,)

enrich_form(UserForm)
