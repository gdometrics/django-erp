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
from django.db.models.query import QuerySet
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey

class _GFKQuerySet(QuerySet):
    def filter(self, **kwargs):
        gfk_fields = [g for g in self.model._meta.virtual_fields if isinstance(g, GenericForeignKey)]

        for gfk in gfk_fields:
            if kwargs.has_key(gfk.name):
                param = kwargs.pop(gfk.name)
                kwargs[gfk.fk_field] = param.pk
                kwargs[gfk.ct_field] = ContentType.objects.get_for_model(param)

        return super(_GFKQuerySet, self).filter(**kwargs)

class _GFKManager(models.Manager):
    def get_query_set(self):
        return _GFKQuerySet(self.model)

class NotificationQuerySet(_GFKQuerySet):
    def read(self):
        return self.filter(read__isnull=False)

    def unread(self):
        return self.filter(read__isnull=True)

    def for_object(self, instance):
        return self.filter(target=instance)
        
    def read_for_object(self, instance):
        return self.for_object(instance).filter(read__isnull=False)

    def unread_for_object(self, instance):
        return self.for_object(instance).filter(read__isnull=True)
        
class FollowRelationManager(_GFKManager):
    pass
    
class SubscriptionManager(_GFKManager):
    pass

class ActivityManager(_GFKManager):
    """Manager for activities.
    """
    def create(self, *args, **kwargs):
        """Create and notifies the activity to all the followers.
        """
        from models import Signature, Subscription, Notification

        source = kwargs.get("source", None)

        instance = super(ActivityManager, self).create(*args, **kwargs)

        content = instance.get_content()
        signature, is_new = Signature.objects.get_or_create(slug=instance.signature)
        followers = source.followers()
        subscribers = [s.subscriber for s in Subscription.objects.filter(signature=signature).distinct()]
        for follower in followers:
            # NOTE: Don't change "==" to "is".
            if (follower == source and instance.source) or (follower in subscribers):
                notification, is_new = Notification.objects.get_or_create(
                    title=u"%s" % instance,
                    description=content,
                    target=follower,
                    signature=signature,
                    dispatch_uid="%d" % instance.pk,
                )

        return instance

class NotificationManager(_GFKManager):
    """Manager for notifications.
    """
    def get_query_set(self):
        return NotificationQuerySet(self.model)

    def read(self):
        return self.get_query_set().read()

    def unread(self):
        return self.get_query_set().unread()

    def for_object(self, instance):
        return self.get_query_set().for_object(instance)
        
    def read_for_object(self, instance):
        return self.get_query_set().read_for_object(instance)

    def unread_for_object(self, instance):
        return self.get_query_set().unread_for_object(instance)
