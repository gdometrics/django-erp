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

from django import forms
from django.utils.translation import ugettext_lazy as _
from djangoerp.core.forms import enrich_form

from models import *

class SubscriptionWidget(forms.MultiWidget):
    """Widget for subscription entry.
    """
    def __init__(self, *args, **kwargs):
        kwargs['widgets'] = (
            forms.CheckboxInput(attrs={'class': 'subscribe'}),
            forms.CheckboxInput(attrs={'class': 'email'})
        )
        super(SubscriptionWidget, self).__init__(*args, **kwargs)

    def decompress(self, value):
        if value:
            return value.values()
        return (False, False)

    def format_output(self, rendered_widgets):
        return '<td>%s</td>' % '</td>\n<td>'.join(rendered_widgets)

class SubscriptionField(forms.MultiValueField):
    """Field for subscription entry.
    """
    widget = SubscriptionWidget

    def __init__(self, *args, **kwargs):
        if 'initial' not in kwargs:
            kwargs['initial'] = {'subscribe': False, 'email': False}
        initial = kwargs['initial']
        kwargs['fields'] = (
            forms.BooleanField(required=False, label=_('subscribe'), initial=initial['subscribe']),
            forms.BooleanField(required=False, label=_('send email'), initial=initial['email'])
        )
        super(SubscriptionField, self).__init__(*args, **kwargs)

    def compress(self, data_list):
        if len(data_list) >= 2:
            return (data_list[0], data_list[1])
        return None

class SubscriptionsForm(forms.Form):
    """Form for notification subscriptions.
    """
    def __init__(self, *args, **kwargs):
        try:
            self.subscriber = kwargs.pop('subscriber')
        except KeyError:
            self.subscriber = None
        super(SubscriptionsForm, self).__init__(*args, **kwargs)
        signatures = Signature.objects.all()
        for signature in signatures:
            name = signature.slug
            is_subscriber = (Subscription.objects.filter(signature=signature, subscriber=self.subscriber).count() > 0)
            send_email = (Subscription.objects.filter(signature=signature, subscriber=self.subscriber, send_email=True).count() > 0)
            field = SubscriptionField(label=_(signature.title), initial={'subscribe': is_subscriber, 'email': send_email})
            self.fields[name] = field
            
    def save(self):
        data = self.cleaned_data
        for key, (subscribe, email) in data.iteritems():
            signature = Signature.objects.get(slug=key)
            is_subscriber = (Subscription.objects.filter(subscriber=self.subscriber, signature=signature).count() > 0)
            if subscribe:
                subscription = Subscription.objects.get_or_create(subscriber=self.subscriber, signature=signature)[0]
                subscription.email = self.subscriber.email
                subscription.send_email = email
                subscription.save()
            elif is_subscriber:
                Subscription.objects.filter(subscriber=self.subscriber, signature=signature).delete()
                self.fields[key].initial = (False, False)
                 
enrich_form(SubscriptionsForm)
