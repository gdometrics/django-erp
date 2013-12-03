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

from django.conf import settings
from django.contrib.auth import get_user_model

from models import *

class ObjectPermissionBackend(object):
    """Backend which enables support for row/object-level permissions.
    
    NOTE: this backend only handles row/object-level permissions. It must works
    in conjunction which Django's model backend, not as a replacement. In fact,
    if a user has only model-level permissions over a certain model (but no
    row/object-level ones for that particular model instance) this backend's
    "has_perm" method will return a negative response.
    """
    supports_object_permissions = True
    supports_anonymous_user = True
    supports_inactive_user = True

    def authenticate(self, username, password):
        # This backend doesn't handle user authentication.
        return None

    def get_group_permissions(self, user_obj):
        """Returns all and only the object perms granted to the groups of the given user_obj.
        """
        if not hasattr(user_obj, '_group_obj_perm_cache'):
            perms = ObjectPermission.objects.get_group_permissions(user_obj)
            perms = perms.values_list('perm__content_type__app_label', 'perm__codename', 'object_id').order_by()
            user_obj._group_obj_perm_cache = set(["%s.%s.%s" % (ct, name, obj_id) for ct, name in perms])
        return user_obj._group_obj_perm_cache

    def get_all_permissions(self, user_obj):
        """Returns all and only the object perms granted to the given user_obj.
        """
        if user_obj.is_anonymous():
            return set()
        if not hasattr(user_obj, '_obj_perm_cache'):
            user_obj._obj_perm_cache = set([p.uid for p in user_obj.objectpermissions.all()])
            user_obj._obj_perm_cache.update(self.get_group_permissions(user_obj))
        return user_obj._obj_perm_cache

    def has_perm(self, user_obj, perm, obj=None):
        """This method checks if the user_obj has perm on obj.
        """
        if user_obj.is_superuser:
            return True

        if not user_obj.is_active:
            return False

        if obj is None:
            return False

        if isinstance(perm, Permission):
            perm = perm.uid

        perms = "%s.%s" % (perm, obj.pk) in self.get_all_permissions(user_obj)
        
        # Fallback to model-level permissions.
        #if not perms:
        #    from django.contrib.auth.backends import ModelBackend
        #    perms = ModelBackend().has_perm(user_obj, perm)
        
        return perms
