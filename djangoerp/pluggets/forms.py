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

class TextPluggetForm(forms.Form):
    """A form to set context variables of text plugget.
    """
    text = forms.CharField(initial=_("Write something here..."), required=True, max_length=100, label=_('Text'))

class SelectPluggetSourceForm(forms.Form):
    """A form to choose the plugget source from registered ones.
    """
    source_uid = forms.ChoiceField(required=True, label=_('Type'))
    
    def __init__(self, *args, **kwargs):
        super(SelectPluggetSourceForm, self).__init__(*args, **kwargs)
        self.fields['source_uid'].choices = get_plugget_source_choices()

class CustomizePluggetSettingsForm(forms.ModelForm):
    """A form to customize the plugget appearance source-specific settings.
    
    Setting fields are added dynamically based on source registered form.
    """
    class Meta:
        model = Plugget
        fields = ['title']
    
    def __init__(self, *args, **kwargs):
        self.region = kwargs.pop("region", None)
        super(CustomizePluggetSettingsForm, self).__init__(*args, **kwargs)
    
    def clean_title(self):
        title = self.cleaned_data['title']
       
        try:
            plugget = Plugget.objects.get(title=title, region=self.region)
            if plugget != self.instance:
                raise forms.ValidationError(_("This title is already in use."))
                
        except Plugget.DoesNotExist:
            pass
            
        return title

enrich_form(SelectPluggetSourceForm)
enrich_form(CustomizePluggetSettingsForm)
