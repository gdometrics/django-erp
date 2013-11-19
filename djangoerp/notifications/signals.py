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

import django.dispatch
from django.db import models
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils.translation import ugettext_noop as _
from django.contrib.auth import get_user_model
from djangoerp.core.utils import get_model
from djangoerp.core.models import Permission, ObjectPermission
from djangoerp.core.cache import LoggedInUserCache

from models import *

## HANDLERS ##

def _cache_followers(sender, instance, **kwargs):
    """Save the follower list in a cache variable.
    """
    if issubclass(sender, Observable):
        if instance._Observable__followers_cache:
            instance._Observable__followers_cache = None
        followers = instance.followers()
        instance._Observable__followers_cache = followers        

def _notify_changes(sender, instance, **kwargs):
    """Notifies one or more changes in an Observable-derived model.
    
    Changes are notified sending a "post_change" signal.
    """
    if issubclass(sender, Observable):

        if kwargs['created']:
            instance.follow(instance)
            for sf in instance._Observable__subscriber_fields:
                if hasattr(instance, sf):
                    follower = getattr(instance, sf)
                    instance.follow(follower)

        else:
            changes = {}
            for name, (old_value, value) in instance._Observable__changes.items():
                if value != old_value:
                    changes[name] = (old_value, value)
                    if name in instance._Observable__subscriber_fields:
                        instance.unfollow(old_value)
                        instance.follow(value)
            instance._Observable__changes = {}
            if changes:
                post_change.send(sender=sender, instance=instance, changes=changes)

def send_notification_email(sender, instance, signal, *args, **kwargs):
    """Sends an email related to the notification.
    """
    if kwargs['created'] and instance.target:
        try:
            subscription = Subscription.objects.get(signature=instance.signature, subscriber=instance.target, send_email=True)
            email_subject = instance.title
            email_body = instance.description
            email_from = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@localhost.com')
            if subscription.email:
                email = EmailMessage(email_subject, email_body, email_from, [subscription.email,])
                email.content_subtype = "html"
                email.send()
        except Subscription.DoesNotExist:
            pass

def update_user_subscription_email(sender, instance, *args, **kwargs):
    """Updates the email address for all the subscription related to this user.
    """
    for s in Subscription.objects.filter(subscriber=instance):
        s.email = instance.email
        s.save()
            
## NOTIFIERS ##

def notify_object_created(sender, instance, *args, **kwargs):
    """Generates an activity related to the creation of a new object.
    """
    if kwargs['created']:
        author = LoggedInUserCache().current_user
        title = _("%(class)s %(name)s created")
        context = {
            "class": sender.__name__.lower(),
            "name": "%s" % instance,
            "link": instance.get_absolute_url(),
        }

        if author:
            title = _("%(class)s %(name)s created by %(author)s")
            context.update({
                "author": "%s" % author,
                "author_link": author.get_absolute_url()
            })

        activity = Activity.objects.create(
            title=title,
            signature="%s-created" % sender.__name__.lower(),
            template="notifications/activities/object-created.html",
            context=json.dumps(context),
            backlink=instance.get_absolute_url(),
            source=instance
        )

def notify_object_changed(sender, instance, changes, *args, **kwargs):
    """Generates an activity related to the change of an existing object.
    """
    author = LoggedInUserCache().current_user
    title = _("%(class)s %(name)s changed")
    context = {
        "class": sender.__name__.lower(),
        "name": "%s" % instance,
        "link": instance.get_absolute_url(),
        "changes": changes
    }

    if author:
        title = _("%(class)s %(name)s changed by %(author)s")
        context.update({
            "author": "%s" % author,
            "author_link": author.get_absolute_url()
        })

    activity = Activity.objects.create(
        title=title,
        signature="%s-changed" % sender.__name__.lower(),
        template="notifications/activities/object-changed.html",
        context=json.dumps(context),
        backlink=instance.get_absolute_url(),
        source=instance
    )

def notify_object_deleted(sender, instance, *args, **kwargs):
    """Generates an activity related to the deletion of an existing object.
    """
    author = LoggedInUserCache().current_user
    title = _("%(class)s %(name)s deleted")
    context = {
        "class": sender.__name__.lower(),
        "name": "%s" % instance
    }

    if author:
        title = _("%(class)s %(name)s deleted by %(author)s")
        context.update({
            "author": "%s" % author,
            "author_link": author.get_absolute_url()
        })

    activity = Activity.objects.create(
        title=title,
        signature="%s-deleted" % sender.__name__.lower(),
        template="notifications/activities/object-deleted.html",
        context=json.dumps(context),
        source=instance
    )

def notify_m2m_changed(sender, instance, action, reverse, model, pk_set, *args, **kwargs):
    """Generates one or more activities related to the change of an existing many-to-many relationship.
    """
    try:
        if action == "post_add":
            for pk in pk_set:
                notify_object_created(sender=model, instance=model.objects.get(pk=pk))

        elif action == "post_remove":
            for pk in pk_set:
                notify_object_deleted(sender=model, instance=model.objects.get(pk=pk))

    except:
        pass

## SIGNALS ##

post_change = django.dispatch.Signal(providing_args=["instance", "changes"])

## UTILS ##

def make_observable(cls, exclude=['modified'], auto_subscriber_fields=['parent', 'author']):
    """Adds Observable mix-in to the given class.

    Should be placed before every other signal connection for the given class.

    @param cls The object class which needs to be observed.
    @param exclude The list of fields to not track in changes.
    @param auto_subscriber_fields The list of fields which should be automatically
                                  added as subscribers.
    """
    cls = get_model(cls)
        
    if not issubclass(cls, Observable):

        class _Observable(Observable):
            __change_exclude = exclude
            __subscriber_fields = auto_subscriber_fields

        cls.__bases__ += (_Observable,)

        models.signals.pre_delete.connect(_cache_followers, sender=cls, dispatch_uid="%s_cache_followers" % cls.__name__)
        models.signals.post_save.connect(_notify_changes, sender=cls, dispatch_uid="%s_notify_changes" % cls.__name__)
        
def make_default_notifier(cls, exclude=['modified'], auto_subscriber_fields=['parent', 'author']):
    """Makes the class observable and notify creation, changing and deletion.

    @param cls The object class which needs to be observed.
    @param exclude The list of fields to not track in changes.
    @param auto_subscriber_fields The list of fields which should be automatically
                                  added as subscribers.
    """
    cls = get_model(cls)
    if not issubclass(cls, Observable):
        make_observable(cls, exclude, auto_subscriber_fields)
        models.signals.post_save.connect(notify_object_created, sender=cls, dispatch_uid="%s_created" % cls.__name__)
        post_change.connect(notify_object_changed, sender=cls, dispatch_uid="%s_changed" % cls.__name__)
        models.signals.m2m_changed.connect(notify_m2m_changed, sender=cls, dispatch_uid="%s_m2m_changed" % cls.__name__)
        models.signals.post_delete.connect(notify_object_deleted, sender=cls, dispatch_uid="%s_deleted" % cls.__name__)
        
def make_notification_target(cls):
    """Adds NotificationTarget mix-in to the given class.

    @param cls The object class.
    """
    cls = get_model(cls)
    if not issubclass(cls, NotificationTarget):
        cls.__bases__ += (NotificationTarget,)

## CONNECTIONS ##

models.signals.post_save.connect(update_user_subscription_email, sender=get_user_model(), dispatch_uid="update_user_subscription_email")
models.signals.post_save.connect(send_notification_email, sender=Notification, dispatch_uid="send_notification_email")

make_notification_target(settings.AUTH_USER_MODEL)
