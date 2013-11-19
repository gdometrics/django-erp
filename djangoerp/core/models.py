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
import re
from django.db import models
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core import validators
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group as DjangoGroup, Permission as DjangoPermission

from managers import *
        
def validate_json(value):
    """Validates a JSON snippet.
    """
    try:
        json.loads(value)
    except:
        raise ValidationError(_('Ivalid JSON syntax'))
        
class User(AbstractBaseUser, PermissionsMixin):
    """A custom User model with timezone and language support.
    """
    username = models.CharField(
        max_length=30,
        unique=True,
        help_text=_('Required. 30 characters or fewer. Letters, numbers and '
                    '@/./+/-/_ characters'),
        validators=[
            validators.RegexValidator(re.compile('^[\w.@+-]+$'), _('Enter a valid username.'), 'invalid')
        ],
        verbose_name=_('username')
    )
    email = models.EmailField(max_length=254, verbose_name=_('email'))
    is_staff = models.BooleanField(default=False, help_text=_('Designates whether the user can log into this admin site.'), verbose_name=_('staff?'))
    is_active = models.BooleanField(default=True, help_text=_('Designates whether this user should be treated as active. Unselect this instead of deleting accounts.'), verbose_name=_('active?'))
    date_joined = models.DateTimeField(default=timezone.now, verbose_name=_('date joined'))
    language = models.CharField(max_length=5, null=True, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE, verbose_name=_("language"))
    timezone = models.CharField(max_length=20, null=True, choices=settings.TIME_ZONES, default=settings.TIME_ZONE, verbose_name=_("timezone"))
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        
    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        self._meta.get_field('is_superuser').verbose_name = _('admin?')

    def get_short_name(self):
        return self.username
    
    @models.permalink
    def get_absolute_url(self):
        return ('user_detail', (), {"pk": self.pk})

    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.email])

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
    users = models.ManyToManyField(User, null=True, blank=True, related_name='objectpermissions', verbose_name=_("users"))
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
