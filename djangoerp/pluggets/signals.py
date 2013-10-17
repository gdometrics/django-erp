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

from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.translation import ugettext_noop as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

from models import *

class _Registry:
    def __init__(self, *args, **kwargs):
        self._classes = {}

    def manage_dashboard(self, cls, default_title=_("Dashboard")):
        """Connects handlers for dashboard management.
        """
        @receiver(post_save, sender=cls)
        def create_dashboard(sender, instance, *args, **kwargs):
            """Creates a new dashboard for the given object.
            """
            model_ct = ContentType.objects.get_for_model(cls)
            dashboard, is_new = Region.objects.get_or_create(
                slug="%s_%d_dashboard" % (model_ct.model, instance.pk),
                title=default_title,
                content_type=model_ct,
                object_id=instance.pk
            )
            
        self._classes[cls] = create_dashboard

registry = _Registry()

# Connections

registry.manage_dashboard(get_user_model(), _('My dashboard'))
