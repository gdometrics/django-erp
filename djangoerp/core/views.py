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

from copy import copy
from django.http import HttpResponseRedirect
from django.views.generic.list import ListView
from django.template.response import TemplateResponse

from utils import clean_http_referer, set_path_kwargs

class SetCancelUrlMixin(object):
    """Mixin that allows to set an URL to "rollback" (cancel) the current view.
    
    It adds a context variable called "back" with the value of "cancel_url" (if
    provided) or the HTTP referer (otherwise).
    """
    cancel_url = None
    
    def get_context_data(self, **kwargs):
        context = super(SetCancelUrlMixin, self).get_context_data(**kwargs)
        context.update({"back": self.request.GET.get('back', self.cancel_url or clean_http_referer(self.request))})
        return context  

class BaseModelListView(ListView):
    """View to be used in conjunction with render_model_list templatetag.
    
    It allows to set two context variables:
    
     * field_list -- The list of fields to be rendererd in the model list.
                     Set the "field_list" variable or overwrite the
                     "get_field_list" method.
     * list_template_name -- The template name for rendering the model list. 
                             Set the "list_template_name" variable or overwrite
                             the "get_list_template_name" method.
     * list_uid -- The unique ID of the model list.
                   Set the "list_uid" variable or overwrite the "get_list_uid"
                   method.
    """
    field_list = None
    list_template_name = "elements/model_list.html"
    list_uid = ""
    
    def __init__(self, fields=None, list_template_name=None, list_uid=None, *args, **kwargs):
        super(BaseModelListView, self).__init__(*args, **kwargs)
        if fields:
            self.field_list = fields
        if list_template_name:
            self.list_template_name = list_template_name
        if list_uid:
            self.list_uid = list_uid
    
    def get_field_list(self):
        return self.field_list
    
    def get_list_template_name(self):
        return self.list_template_name
    
    def get_list_uid(self):
        return self.list_uid
        
    def get_list_prefix(self):
        uid = self.get_list_uid()
        if uid:
            return "%s_" % uid
        
        return ""
        
    def paginate_queryset(self, queryset, page_size):
        self.page_kwarg = "%spage" % self.get_list_prefix()
        return super(BaseModelListView, self).paginate_queryset(queryset, page_size)
    
    def get_context_data(self, *args, **kwargs):
        context = super(BaseModelListView, self).get_context_data(*args, **kwargs)
        context['field_list'] = self.get_field_list()
        context['list_template_name'] = self.get_list_template_name()
        context['list_uid'] = self.get_list_uid()
        return context

class ModelListDeleteMixin(object):
    """Mixin to be used with "ModelListView" to delete a group of list items.
    
    It manages deletion of one or more model instances at the same time.
    
    It could be customize using the following context variables:
    
     * delete_template_name -- The template name which is used to renders the
                               deletion confrimation page. 
                               Set the "delete_template_name" variable or
                               overwrite the "get_delete_template_name" method.
    """
    delete_template_name = "base_model_list_confirm_delete.html"
        
    def get_selected_uids(self, request, *args, **kwargs):
        selected_uids = []
        prefix = self.get_list_prefix()
        selected_all = request.POST.get("%sselect_all" % prefix, False)
        
        if selected_all:
            selected_uids = "*"
            
        else:
            for k, v in request.POST.items():
                if k.startswith("%sselect_" % prefix) and v:
                    selected_uids.append(k.rpartition('_')[2])
                    
        return selected_uids
        
    def get_delete_template_name(self):
        return self.delete_template_name

    def delete_selected(self, request, *args, **kwargs):
        prefix = self.get_list_prefix()
        selected_uids = self.get_selected_uids(request, *args, **kwargs)
        queryset = self.get_queryset()
        selected_queryset = queryset
        if hasattr(queryset, '_clone'):
            selected_queryset = queryset._clone()
          
        if isinstance(selected_uids, list):
            selected_queryset = selected_queryset.filter(pk__in=selected_uids)   
        
        if selected_queryset:
            if "%sdelete_selected" % prefix in request.POST:
                return TemplateResponse(request, self.get_delete_template_name(), {"object_list": selected_queryset})

            if "%sconfirm_delete_selected" % prefix in request.POST:
                selected_queryset.delete()
                curr_page = request.GET.get(self.page_kwarg, 1)
                page_size = self.get_paginate_by(queryset)
                item_count = queryset.count()
                page_count = item_count / page_size
                if item_count % page_size > 0:
                    page_count += 1
                if curr_page > page_count:
                    path = set_path_kwargs(request, **{self.page_kwarg: page_count})
                    return HttpResponseRedirect(path, *args, **kwargs)
        
        return self.get(request, *args, **kwargs)
        
    def post(self, request, *args, **kwargs):
        selected_uids = self.get_selected_uids(request, *args, **kwargs)
        
        if selected_uids\
        and ("%sdelete_selected" % self.get_list_prefix() in request.POST\
            or "%sconfirm_delete_selected" % self.get_list_prefix() in request.POST):
            return self.delete_selected(request, *args, **kwargs)
            
        return super(ModelListDeleteMixin, self).post(request, *args, **kwargs)
        
class ModelListFilteringMixin(object):
    """Mixin to be used with "ModelListView" to filter the list items.
    """
    def get_queryset(self):
        qs = super(ModelListFilteringMixin, self).get_queryset()
        
        filter_query = self.get_filter_query_from_get()
        
        if filter_query:
            return qs.filter(**filter_query)
            
        return qs
    
    def get_context_data(self, *args, **kwargs):
        context = super(ModelListFilteringMixin, self).get_context_data(*args, **kwargs)
        filter_query = self.get_filter_query_from_get()
        context['unfiltered_object_list'] = super(ModelListFilteringMixin, self).get_queryset()
        context['%slist_filter_by' % self.get_list_prefix()] = dict([(k.rpartition('__')[0] or k.rpartition('__')[2], (k.rpartition('__')[2], v)) for k, v in filter_query.items()]) or None
        return context
        
    def post(self, request, *args, **kwargs):
        list_prefix = self.get_list_prefix()
        filter_by_key = "%sfilter_by_" % list_prefix
        filter_query = self.get_filter_query_from_post()
        filter_kwargs = dict([('%s%s' % (filter_by_key, k), v) for k, v in filter_query.items()])
                
        if "%sreset_filters" % list_prefix in request.POST:
            for k, v in filter_kwargs.items():
                filter_kwargs[k] = None
                    
        return HttpResponseRedirect(set_path_kwargs(request, **filter_kwargs), *args, **kwargs)
        
    def get_filter_query_from_post(self):
        filter_query = {}
        list_prefix = self.get_list_prefix()
        filter_arg_name_prefix = "%sfilter_by_" % list_prefix
        filter_arg_expr_prefix = "%sfilter_expr_" % list_prefix
        for arg_name, arg_value in self.request.POST.items():
            if arg_name.startswith(filter_arg_name_prefix):
                arg_name = arg_name.replace(filter_arg_name_prefix, "")
                arg_expr = self.request.POST.get(filter_arg_expr_prefix + arg_name, None)
                arg = arg_name
                if arg_expr:
                    arg += "__%s" % arg_expr
                filter_query.update({arg: arg_value})
        return filter_query
        
    def get_filter_query_from_get(self):
        filter_query = {}
        list_prefix = self.get_list_prefix()
        filter_arg_name_prefix = "%sfilter_by_" % list_prefix
        for arg_name, arg_value in self.request.GET.items():
            if arg_value and arg_name.startswith(filter_arg_name_prefix):
                arg_name = arg_name.replace(filter_arg_name_prefix, "")
                filter_query.update({arg_name: arg_value})
        return filter_query
  
class ModelListOrderingMixin(object):
    """Mixin to be used with "ModelListView" to order the list items.
    """        
    def get_queryset(self):
        qs = super(ModelListOrderingMixin, self).get_queryset()
            
        ord_arg_name = "%sorder_by" % self.get_list_prefix()
        self._order_query = self.request.GET.get(ord_arg_name, None)
        
        if self._order_query:
            return qs.order_by(self._order_query)
            
        return qs
    
    def get_context_data(self, *args, **kwargs):
        context = super(ModelListOrderingMixin, self).get_context_data(*args, **kwargs)
        context['list_order_by'] = self._order_query or None
        return context      
        
class ModelListView(ModelListDeleteMixin, ModelListOrderingMixin, ModelListFilteringMixin, BaseModelListView):
    """Default model list view with support for deleting and ordering.
    """
    pass
