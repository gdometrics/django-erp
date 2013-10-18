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

import json

from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.contrib.formtools.wizard.views import SessionWizardView
from django.views.generic.edit import DeleteView
from djangoerp.core.views import SetCancelUrlMixin, SetSuccessUrlMixin

from loading import registry
from models import *
from forms import *

class PluggetWizard(SessionWizardView):
    DEFAULT_FORMS = [SelectPluggetSourceForm, CustomizePluggetSettingsForm]
    template_name = "pluggets/plugget_wizard_form.html"
    instance = None
    source = None
    region = None
    
    def get_form_initial(self, step):
        initial = super(PluggetWizard, self).get_form_initial(step)
        source_uid = None
        title = None
        
        data0 = self.storage.get_step_data("0")
        data1 = self.storage.get_step_data("1")
        sources = registry.sources
        
        if "pk" in self.kwargs:
            self.instance = get_object_or_404(Plugget, pk=self.kwargs['pk'])
            self.region = self.instance.region
            source_uid = self.instance.source
            title = self.instance.title
            if data0:
                source_uid = data0.get(u'0-source_uid', self.instance.source)
            self.source = sources.get(source_uid, {})
            self.source['source_uid'] = source_uid
            if data1:
                title = data1.get(u'1-title', self.instance.title)
            
        elif "slug" in self.kwargs:
            self.region = get_object_or_404(Region, slug=self.kwargs['slug'])
            if data0:
                source_uid = data0.get(u'0-source_uid', None)
            self.source = sources.get(source_uid, {})
            self.source['source_uid'] = source_uid
            if data1:
                title = data1.get(u'1-title', self.source['title'])

        if step == "0":
            initial['region_slug'] = self.region.slug
            initial['source_uid'] = source_uid
                
        elif step == "1":
            initial['title'] = title or self.source['title']
            context = self.source['context']
            if self.instance:
                context.update(json.loads(self.instance.context))
            for k, v in context.items():
                initial['context_%s' % k] = v
            
        return initial
        
    def get_context_data(self, form, **kwargs):
        context = super(PluggetWizard, self).get_context_data(form=form, **kwargs)
        context.update({'object': self.instance, 'region': self.region})
        if self.steps.current == '1':
            context.update({
                "plugget_description": self.source['description'],
            })
        return context
            
    def done(self, form_list, **kwargs):
        from django.http import HttpResponseRedirect
        
        # First step:
        f0 = form_list[0]
        
        source_uid = f0.cleaned_data['source_uid']
        source = registry.sources[source_uid]
        
        # Second step:
        f1 = form_list[1]
            
        title = f1.cleaned_data['title']
        context = {}
        
        for k, v in f1.cleaned_data.items():
            if k.startswith("context_"):
                context[k.replace("context_", "")] = v
                
        context = json.dumps(context)
        
        # Merging:
        if self.instance:
            self.instance.source = source_uid
            self.instance.title = title
            self.instance.context = context
            self.instance.template = source['default_template']
            self.instance.description = source['description']
            self.instance.save()
        
        else:
            region = get_object_or_404(Region, slug=kwargs.get('slug', None))
            self.instance = Plugget.objects.create(
                source=source_uid,
                region=region,
                title=title,
                context=context,
                description=source['description'],
                template=source['default_template'],
                sort_order=region.pluggets.count()
            )
            
        return HttpResponseRedirect(self.instance.get_absolute_url())
        
class DeletePluggetView(SetCancelUrlMixin, SetSuccessUrlMixin, DeleteView):
    model = Plugget

