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

from django.dispatch import receiver
from django.utils.translation import ugettext_noop as _
from django.db.models.signals import post_save, pre_delete
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from djangoerp.core.signals import manage_author_permissions

from models import *

class _DashboardRegistry:
    def __init__(self, *args, **kwargs):
        self._classes = {}

    def manage_dashboard(self, cls, default_title):
        """Connects handlers for dashboard management.
        """        
        @receiver(post_save, sender=cls, dispatch_uid="create_%s_dashboard" % cls)
        def create_dashboard(sender, instance, *args, **kwargs):
            """Creates a new dashboard for the given object.
            """            
            from djangoerp.core.cache import LoggedInUserCache
            
            logged_cache = LoggedInUserCache()
            current_user = logged_cache.current_user
            
            if isinstance(instance, get_user_model()):
                logged_cache.user = instance
                
            model_ct = ContentType.objects.get_for_model(cls)
            dashboard, is_new = Region.objects.get_or_create(
                slug="%s_%d_dashboard" % (model_ct.model, instance.pk),
                title=default_title,
                content_type=model_ct,
                object_id=instance.pk
            )
            
            logged_cache.user = current_user
            
        @receiver(pre_delete, sender=cls, dispatch_uid="delete_%s_dashboard" % cls)
        def delete_dashboard(sender, instance, *args, **kwargs):
            try:
                model_ct = ContentType.objects.get_for_model(cls)
                dashboard = Region.objects.get(slug="%s_%d_dashboard" % (model_ct.model, instance.pk))
                dashboard.delete()
            except Region.DoesNotExist:
                pass
            
        self._classes[cls] = (create_dashboard, delete_dashboard)

_dashboard_registry = _DashboardRegistry()

def manage_dashboard(cls, default_title=_("Dashboard")):
    """Connects handlers for dashboard management.
    
    This handler could be used to automatically create a related dashboard on
    given model class instance creation. i.e.:
    
    >> manage_dashboard(Project, _("Project's dashboard"))
        
    It will auto generate a dashboard associated to each new Project's instance
    with title "Project's dashboard". If no title is passed, default title will
    be used ("Dashboard").
    """
    _dashboard_registry.manage_dashboard(cls, default_title)

## CONNECTIONS ##

manage_author_permissions(Region)
manage_author_permissions(Plugget)

manage_dashboard(get_user_model(), _('My dashboard'))

