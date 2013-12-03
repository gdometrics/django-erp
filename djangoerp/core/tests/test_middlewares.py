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
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from . import *
from ..middleware import *
        
class RequireLoginMiddlewareTestCase(TestCase):
    pass
    
class LoggedInUserCacheMiddlewareTestCase(TestCase):
    def test_store_request_user(self):
        """Tests the correct storing of the current user in the logged cache.
        """
        r = FakeRequest()
        m = LoggedInUserCacheMiddleware()
        u, n = get_user_model().objects.get_or_create(username="u1")
        m.process_request(r)
        
        self.assertTrue(isinstance(logged_cache.user, AnonymousUser))
        self.assertFalse(logged_cache.has_user)
        
        r.user = u
        m.process_request(r)
        
        self.assertEqual(logged_cache.user, u)
        self.assertTrue(logged_cache.has_user)
        
        # Reset (WARNING: DON'T REMOVE!).
        r.user = AnonymousUser()
        m.process_request(r)
