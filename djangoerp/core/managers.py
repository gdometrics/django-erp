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

from django.db import models
from django.db.models import Q, get_model, get_models, get_app
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager, PermissionManager as DjangoPermissionManager
from django.contrib.contenttypes.models import ContentType

class UserManager(BaseUserManager):
    """Manager for custom User model.
    """
    def _create_user(self, username, email, password, is_staff, is_superuser, **extra_fields):
        """Creates and saves a User with the given email and password.
        """
        now = timezone.now()
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        user = self.model(
            username=username,
            email=email,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            last_login=now,
            date_joined=now,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email, password=None, **extra_fields):
        return self._create_user(username, email, password, False, False, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        return self._create_user(username, email, password, True, True, **extra_fields)

class PermissionManager(DjangoPermissionManager):
    """Custom manager for Permission model.
    """
    def get_or_create_by_natural_key(self, codename, app_label, model):
        from models import Permission
        get_models(get_app(app_label))
        ct = ContentType.objects.get_for_model(get_model(app_label, model))
        action, sep, model_name = codename.rpartition('_')
        name = "Can %s %s" % (action.replace('_', ' '), ct.name)
        return Permission.objects.get_or_create(codename=codename, name=name, content_type=ct)
        
    def get_by_uid(self, uid):
        app_label, sep, codename = uid.rpartition('.')
        return self.get_by_natural_key(codename, app_label, codename.rpartition('_')[2])
        
    def get_or_create_by_uid(self, uid):
        app_label, sep, codename = uid.rpartition('.')
        return self.get_or_create_by_natural_key(codename, app_label, codename.rpartition('_')[2])
        

class ObjectPermissionManager(models.Manager):
    """Custom manager for ObjectPermission model.
    """
    def get_by_natural_key(self, codename, app_label, model, object_id):
        perm = PermissionManager().get_by_natural_key(codename, app_label, model)
        return self.get(perm=perm, object_id=int(object_id))

    def get_or_create_by_natural_key(self, codename, app_label, model, object_id):
        perm, is_new = PermissionManager().get_or_create_by_natural_key(codename, app_label, model)
        return self.get_or_create(perm=perm, object_id=int(object_id))
        
    def get_by_uid(self, uid):
        tokens = uid.split('.')
        return self.get_by_natural_key(tokens[1], tokens[0], tokens[1].rpartition('_')[2], tokens[2])
        
    def get_or_create_by_uid(self, uid):
        tokens = uid.split('.')
        return self.get_or_create_by_natural_key(tokens[1], tokens[0], tokens[1].rpartition('_')[2], tokens[2])

    def get_group_permissions(self, user):
        return self.filter(groups__user=user)

    def get_all_permissions(self, user):
        return self.filter(Q(groups__user=user) | Q(users=user))
