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

from django import forms
from django.utils.translation import ugettext_lazy as _
from djangoerp.core.forms import enrich_form

from models import *
from loading import registry

class SelectPluggetSourceForm(forms.Form):
    """A form to choose the plugget source from registered ones.
    """
    source_uid = forms.ChoiceField(required=True, choices=registry.get_source_choices(), label=_('Type'))

class CustomizePluggetSettingsForm(forms.Form):
    """A form to customize the plugget appearance source-specific settings.
    
    Setting fields are generated dynamically based on source default context.
    """
    title = forms.CharField(required=True, max_length=100, label=_('Title'))
    
    def __init__(self, *args, **kwargs):
        super(CustomizePluggetSettingsForm, self).__init__(*args, **kwargs)
        for k, v in kwargs['initial'].items():
            if k.startswith("context_"):
                self.fields[k] = forms.CharField(initial=v, max_length=200, label=_(k.replace("context_", "").capitalize()))

enrich_form(SelectPluggetSourceForm)
enrich_form(CustomizePluggetSettingsForm)
