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

import datetime
import random
import hashlib
from django.conf import settings
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from djangoerp.core.models import User

from models import *

def user_post_registration(sender, instance, signal, *args, **kwargs):
    if kwargs['created'] \
    and not instance.is_active:     
        token, is_new = ActivationToken.objects.get_or_create(user=instance)
        if is_new:
            # Creates an activation key.
            sha = hashlib.sha1()
            sha.update(str(random.random()))
            sha.update(instance.username)
            token.activation_key = sha.hexdigest()
            token.key_expiration = datetime.datetime.today() + datetime.timedelta(settings.AUTH_ACTIVATION_EXPIRATION_DAYS)
            token.save()
            
            # Send an activation email.
            current_site = Site.objects.get_current()
            activation_link = 'http://' + current_site.domain + reverse('user_activate', args=[token.activation_key])
            context = {
                "user_name": instance.username,
                "current_site": current_site.name,
                "expiration_time": settings.AUTH_ACTIVATION_EXPIRATION_DAYS,
                "activation_link": activation_link
            }
            email_subject = _(settings.AUTH_ACTIVATION_EMAIL_TITLE) % {"site_name": current_site.name}
            email_body = render_to_string("registration/emails/activation.html", context)
            email_from = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@%s' % current_site.domain)
            email = EmailMessage(email_subject, email_body, email_from, [instance.email,])
            email.content_subtype = "html"
            email.send()

post_save.connect(user_post_registration, sender=User)
