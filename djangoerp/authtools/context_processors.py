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

from django.utils.functional import lazy

from models import *

# ObjPermWrapper and ObjPermLookupDict proxy the permissions system into objects
# the template system could understand.

class ObjPermLookupDict(object):
    def __init__(self, user, module_name):
        self.user, self.module_name = user, module_name

    def __repr__(self):
        return str([p for p in self.user.get_all_permissions() if len(p.split('.')) == 3])

    def __getitem__(self, perm_name):
        if self.user.is_superuser:
            perms = Permission.objects.filter(content_type__app_label=self.module_name, codename=perm_name)
            return [obj.pk for p in perms for obj in p.content_type.model_class().objects.all()]
        return [p.object_id for p in self.user.objectpermissions.filter(perm__content_type__app_label=self.module_name, perm__codename=perm_name)]

    def __nonzero__(self):
        if self.user.is_superuser:
            return True
        return self.user.objectpermissions.filter(perm__contentype__app_label=self.module_name).exists()


class ObjPermWrapper(object):
    def __init__(self, user):
        self.user = user

    def __getitem__(self, module_name):
        return ObjPermLookupDict(self.user, module_name)

    def __iter__(self):
        # I am large, I contain multitudes.
        raise TypeError("ObjPermWrapper is not iterable.")

def auth(request):
    """Adds a new 'obj_perms' context variable.

    If there is no 'user' attribute in the request, uses AnonymousUser (from
    django.contrib.auth).
    """
    # If we access request.user, request.session is accessed, which results in
    # 'Vary: Cookie' being sent in every request that uses this context
    # processor, which can easily be every request on a site if
    # TEMPLATE_CONTEXT_PROCESSORS has this context processor added.  This kills
    # the ability to cache.  So, we carefully ensure these attributes are lazy.
    # We don't use django.utils.functional.lazy() for User, because that
    # requires knowing the class of the object we want to proxy, which could
    # break with custom auth backends.  LazyObject is a less complete but more
    # flexible solution that is a good enough wrapper for 'User'.
    def get_user():
        if hasattr(request, 'user'):
            return request.user
        else:
            from django.contrib.auth.models import AnonymousUser
            return AnonymousUser()

    return {
        'obj_perms':  lazy(lambda: ObjPermWrapper(get_user()), ObjPermWrapper)(),
    }
