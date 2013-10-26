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

from djangoerp.core.utils.dependencies import check_dependency

check_dependency('django.contrib.auth')
check_dependency('django.contrib.contenttypes')
check_dependency('django.contrib.comments')
check_dependency('djangoerp.core')

from django.utils.translation import ugettext_noop as _
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from models import *

def install(sender, **kwargs):    
    # Groups.
    users_group, is_new = Group.objects.get_or_create(
        name=_('users')
    )

def user_post_save(sender, instance, signal, *args, **kwargs):
    """Add view/delete/change object permissions to users (on themselves).
    """
    can_view_this_user, is_new = ObjectPermission.objects.get_or_create_by_natural_key("view_user", "auth", "user", instance.pk)
    can_change_this_user, is_new = ObjectPermission.objects.get_or_create_by_natural_key("change_user", "auth", "user", instance.pk)
    can_delete_this_user, is_new = ObjectPermission.objects.get_or_create_by_natural_key("delete_user", "auth", "user", instance.pk)
    can_view_this_user.users.add(instance)
    can_change_this_user.users.add(instance)
    can_delete_this_user.users.add(instance)

def add_view_permission(sender, instance, **kwargs):
    """Adds a view permission related to each new ContentType instance.
    """
    if isinstance(instance, ContentType):
        codename = "view_%s" % instance.model
        Permission.objects.get_or_create(content_type=instance, codename=codename, name="Can view %s" % instance.name)

post_save.connect(user_post_save, get_user_model())
post_save.connect(add_view_permission, ContentType)
