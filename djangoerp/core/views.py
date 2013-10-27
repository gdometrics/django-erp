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

from django.views.generic.list import ListView
from django.template.response import TemplateResponse

from utils import clean_http_referer

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
    
    def get_context_data(self, *args, **kwargs):
        context = super(BaseModelListView, self).get_context_data(*args, **kwargs)
        context['field_list'] = self.get_field_list()
        context['list_template_name'] = self.get_list_template_name()
        context['list_uid'] = self.get_list_uid()
        if context['list_uid']:
            self.page_kwarg = context['list_uid'] + "_page"
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
          
        if isinstance(selected_uids, list):
            queryset = queryset.filter(pk__in=selected_uids)   
        
        if "%sdelete_selected" % prefix in request.POST and queryset:
            return TemplateResponse(request, self.get_delete_template_name(), {"object_list": queryset})

        if queryset:
            queryset.delete()
        
        return self.get(request, *args, **kwargs)
        
class ModelListOrderingMixin(object):
    """Mixin to be used with "ModelListView" to order the list items.
    """        
    def get_queryset(self):
        qs = super(ModelListOrderingMixin, self).get_queryset()
        
        ord_fields = self.field_list
            
        ord_arg_name = "%sorder_by" % self.get_list_prefix()
        self._order_query = self.request.GET.get(ord_arg_name, None)
        
        if self._order_query:
            return qs.order_by(self._order_query)
            
        return qs
    
    def get_context_data(self, *args, **kwargs):
        context = super(ModelListOrderingMixin, self).get_context_data(*args, **kwargs)
        context['list_order_by'] = self._order_query or None
        return context      
        
class ModelListView(ModelListOrderingMixin, ModelListDeleteMixin, BaseModelListView):
    """Default model list view with support for deleting and ordering.
    """
    pass
