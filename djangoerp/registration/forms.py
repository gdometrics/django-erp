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
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from djangoerp.core.forms import UserForm

class UserRegistrationForm(UserForm):
    """Form for user registration.
    """
    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)        
        # Improved security.
        if hasattr(self.fields, 'is_admin'): self.fields.pop('is_admin')
        if hasattr(self.fields, 'is_staff'): self.fields.pop('is_staff')
        if hasattr(self.fields, 'is_active'): self.fields.pop('is_active')
        if hasattr(self.fields, 'is_superuser'): self.fields.pop('is_superuser')
        if hasattr(self.fields, 'groups'): self.fields.pop('groups')
        if hasattr(self.fields, 'user_permissions'): self.fields.pop('user_permissions')
    
    
