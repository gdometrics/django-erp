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
from django.contrib.auth.models import AnonymousUser

from ..cache import LoggedInUserCache
from ..backends import *

user_model_string = settings.AUTH_USER_MODEL
auth_app, sep, user_model_name = user_model_string.rpartition('.')
ob = ObjectPermissionBackend()
logged_cache = LoggedInUserCache()

def clear_perm_caches(user):
    """Helper function which clears perms caches of the given user.
    """
    if hasattr(user, '_perm_cache'):
        delattr(user, '_perm_cache')
    if hasattr(user, '_group_perm_cache'):
        delattr(user, '_group_perm_cache')
    if hasattr(user, '_obj_perm_cache'):
        delattr(user, '_obj_perm_cache')
    if hasattr(user, '_group_obj_perm_cache'):
        delattr(user, '_group_obj_perm_cache')

class FakeRequest(object):
    def __init__(self):
        self.user = None
        self.META = {'HTTP_HOST': "myhost.com", 'HTTP_REFERER': "http://www.test.com"}
