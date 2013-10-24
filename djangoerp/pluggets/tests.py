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

from django.utils import unittest
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from loading import get_plugget_sources
from models import Region, Plugget

class SourceCacheLoadingTestCase(unittest.TestCase):
    def test_source_cache_auto_discovering(self):
        """Tests the auto-discovering of plugget sources.
        """
        self.assertTrue("djangoerp.pluggets.pluggets.text" in get_plugget_sources())        

class RegionTestCase(unittest.TestCase):
    def test_get_absolute_url_without_owner(self):
        """Tests the "get_absolute_url" method of a region without owner object.
        """
        r1, n = Region.objects.get_or_create(slug="r1")
        self.assertEqual(r1.get_absolute_url(), "/")
        
    def test_get_absolute_url_with_user_as_owner(self):
        """Tests the "get_absolute_url" method of a region with an owner object.
        """
        u1, n = get_user_model().objects.get_or_create(username="u1")
        ct = ContentType.objects.get_for_model(u1)
        r2, n = Region.objects.get_or_create(slug="r2", content_type=ct, object_id=u1.pk)
        self.assertNotEqual(r2.get_absolute_url(), u1.get_absolute_url())
        self.assertEqual(r2.get_absolute_url(), "/")
        
    def test_get_absolute_url_with_owner(self):
        """Tests the "get_absolute_url" method of a region with an owner object.
        """
        # TODO: use a custom model as owner of a region.
        pass

class PluggetTestCase(unittest.TestCase):
    def test_get_absolute_url(self):
        """Tests the "get_absolute_url" method of a plugget.
        """
        r1, n = Region.objects.get_or_create(slug="r1")
        p1, n = Plugget.objects.get_or_create(region=r1, title="p1", source="djangoerp.pluggets.base.dummy", template="pluggets/base_plugget.html")
        self.assertEqual(p1.get_absolute_url(), r1.get_absolute_url())
