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

from utils.dependencies import check_dependency

check_dependency('django.contrib.auth')
check_dependency('django.contrib.contenttypes')
check_dependency('django.contrib.sessions')
check_dependency('django.contrib.sites')
check_dependency('django.contrib.messages')
check_dependency('django.contrib.staticfiles')
check_dependency('django.contrib.admin')
check_dependency('django.contrib.admindocs')
check_dependency('django.contrib.comments')
check_dependency('django.contrib.markup')
check_dependency('django.contrib.redirects')
check_dependency('django.contrib.formtools')

from django.utils.translation import ugettext_noop as _
from django.db.models.signals import post_save
from django.contrib.contenttypes.models import ContentType

from models import Group

def install(sender, **kwargs):    
    # Groups.
    users_group, is_new = Group.objects.get_or_create(
        name=_('users')
    )
    
from signals import *
