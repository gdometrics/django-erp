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
from django.contrib.contenttypes.models import ContentType
from djangoerp.core.forms import enrich_form

from models import *
from loading import get_plugget_source_choices

class SelectPluggetSourceForm(forms.Form):
    """A form to choose the plugget source from registered ones.
    """
    source_uid = forms.ChoiceField(required=True, label=_('Type'))
    
    def __init__(self, *args, **kwargs):
        super(SelectPluggetSourceForm, self).__init__(*args, **kwargs)
        self.fields['source_uid'].choices = get_plugget_source_choices()

class CustomizePluggetSettingsForm(forms.Form):
    """A form to customize the plugget appearance source-specific settings.
    
    Setting fields are generated dynamically based on source default context.
    """
    title = forms.CharField(required=True, max_length=100, label=_('Title'))
    
    def __init__(self, *args, **kwargs):
        super(CustomizePluggetSettingsForm, self).__init__(*args, **kwargs)
        for k, v in kwargs['initial'].items():
            if k.startswith("context_"):
                cleaned_k = k[len("context_"):]
                required = cleaned_k[0] is '!'
                if required:
                    cleaned_k = cleaned_k[1:]
                    
                # Foreign key to a model instance.
                if cleaned_k.endswith(".pk"):
                    cleaned_k = cleaned_k[:-len(".pk")]
                    app_label, sep, model_name = cleaned_k.rpartition('.')
                    model_class = ContentType.objects.get_by_natural_key(app_label, model_name).model_class()
                    self.fields[k] = forms.models.ChoiceField(required=required, initial=v, choices=[(i.pk, "%s" % i) for i in model_class.objects.all()], label=model_class.__name__)
                    
                else:
                    self.fields[k] = forms.CharField(initial=v, max_length=200, label=_(k.replace("context_", "").capitalize()))

enrich_form(SelectPluggetSourceForm)
enrich_form(CustomizePluggetSettingsForm)
