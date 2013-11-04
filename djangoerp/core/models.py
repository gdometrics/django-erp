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

import json
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group as DjangoGroup, Permission as DjangoPermission
from django.utils.translation import ugettext_lazy as _

from managers import *
        
def validate_json(value):
    """Validates a JSON snippet.
    """
    try:
        json.loads(value)
    except:
        raise ValidationError(_('Ivalid JSON syntax'))

class Group(DjangoGroup):
    """A proxy for Group model which customize its string representation.
    """
    class Meta:
        proxy = True
        
    def __unicode__(self):
        return _(super(Group, self).__unicode__())

class Permission(DjangoPermission):
    """A proxy for Permission model which uses a custom manager.
    """
    objects = PermissionManager()
    
    class Meta:
        proxy = True
        
    @property
    def uid(self):
        return u"%s.%s" % (self.content_type.app_label, self.codename)

class ObjectPermission(models.Model):
    """A generic object/row-level permission.
    """
    object_id = models.PositiveIntegerField()
    perm = models.ForeignKey(Permission, verbose_name=_("permission"))
    users = models.ManyToManyField(get_user_model(), null=True, blank=True, related_name='objectpermissions', verbose_name=_("users"))
    groups = models.ManyToManyField(Group, null=True, blank=True, related_name='objectpermissions', verbose_name=_("groups"))

    objects = ObjectPermissionManager()

    class Meta:
        verbose_name = _('object permission')
        verbose_name_plural = _('object permissions')
        
    @property
    def uid(self):
        return u"%s.%s" % (self.perm.uid, self.object_id)

    def __unicode__(self):
        return "%s | %d" % (self.perm, self.object_id)
