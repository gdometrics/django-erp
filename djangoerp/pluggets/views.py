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

from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from djangoerp.core.views import SetCancelUrlMixin, SetSuccessUrlMixin

from models import *
from forms import *
    
class RegionAddPluggetView(SetCancelUrlMixin, SetSuccessUrlMixin, CreateView):
    model = Plugget
    form_class = PluggetForm
    
    def get_context_data(self, **kwargs):    
        context = super(RegionAddPluggetView, self).get_context_data(**kwargs)
        region = get_object_or_404(Region, slug=self.kwargs['slug'])
        self.backlink = region.get_absolute_url()
        context['region'] = region
        return context
    
    def form_valid(self, form):
        form.instance.region = get_object_or_404(Region, slug=self.kwargs['slug'])
        return super(RegionAddPluggetView, self).form_valid(form)
        
class UpdatePluggetView(SetCancelUrlMixin, SetSuccessUrlMixin, UpdateView):
    model = Plugget
    form_class = PluggetForm
    
    def get_context_data(self, **kwargs):    
        context = super(UpdatePluggetView, self).get_context_data(**kwargs)
        region = context['object'].region
        self.backlink = region.get_absolute_url()
        context['region'] = region
        return context
        
class DeletePluggetView(SetCancelUrlMixin, SetSuccessUrlMixin, DeleteView):
    model = Plugget

