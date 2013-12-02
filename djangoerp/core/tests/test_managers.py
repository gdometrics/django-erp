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

from django.test import TestCase

from . import *
from ..models import ObjectPermission

class ObjectPermissionManagerTestCase(TestCase):
    def test_get_or_create_perm_by_natural_key(self):
        """Tests "ObjectPermissionManager.get(_or_create)_by_natural_key" method.
        """
        op, n = ObjectPermission.objects.get_or_create_by_natural_key("view_user", auth_app, "user", 1)
        
        self.assertEqual(op.perm.content_type.app_label, auth_app)
        self.assertEqual(op.perm.content_type.model, "user")
        self.assertEqual(op.perm.codename, "view_user")
        self.assertEqual(op.object_id, 1)
        
    def test_get_or_create_perm_by_uid(self):
        """Tests "ObjectPermissionManager.get(_or_create)_by_uid" method.
        """
        op, n = ObjectPermission.objects.get_or_create_by_uid("%s.view_user.1" % auth_app)
        
        self.assertEqual(op.perm.content_type.app_label, auth_app)
        self.assertEqual(op.perm.content_type.model, "user")
        self.assertEqual(op.perm.codename, "view_user")
        self.assertEqual(op.object_id, 1)
