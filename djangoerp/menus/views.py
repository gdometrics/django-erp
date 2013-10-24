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
from django.utils.decorators import method_decorator
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.template.defaultfilters import slugify
from djangoerp.core.utils import clean_http_referer
from djangoerp.core.views import SetCancelUrlMixin, SetSuccessUrlMixin, QuerysetDeleteMixin, ModelListView
from djangoerp.authtools.decorators import obj_permission_required as permission_required

from utils import get_bookmarks_for
from models import *
from forms import *

def _get_bookmarks(request, *args, **kwargs):
    return get_bookmarks_for(request.user.username)

def _get_bookmark(request, *args, **kwargs):
    bookmarks = _get_bookmarks(request, *args, **kwargs)
    return get_object_or_404(Bookmark, slug=kwargs.get('slug', None), menu=bookmarks)
    
class BookmarkMixin(SetCancelUrlMixin, SetSuccessUrlMixin):
    model = Bookmark
    
class BookmarkCreateUpdateMixin(BookmarkMixin):
    form_class = BookmarkForm  
    
    def get_initial(self):
        initial = super(BookmarkCreateUpdateMixin, self).get_initial()
        if not self.object:
            initial["url"] = clean_http_referer(self.request)    
                
        return initial

    def form_valid(self, form):
        menu =  _get_bookmarks(self.request, *self.args, **self.kwargs)
        self.object = form.save(commit=False)
        self.object.menu = menu
        self.object.slug = slugify(("%s_%s" % (self.object.title, self.object.menu.slug))[:-1])
        self.object.save()
        
        return super(BookmarkCreateUpdateMixin, self).form_valid(form)
    
class ListBookmarkView(BookmarkMixin, QuerysetDeleteMixin, ModelListView):
    field_list = ["title", "url", "description", "new_window"]
    delete_template_name = "menus/bookmark_model_list_confirm_delete.html"
    
    @method_decorator(permission_required("menus.view_menu", _get_bookmarks))
    def dispatch(self, request, *args, **kwargs):
        return super(ListBookmarkView, self).dispatch(request, *args, **kwargs)
        
    def post(self, request, *args, **kwargs):
        return self.delete_selected(request, *args, **kwargs) 
    
class CreateBookmarkView(BookmarkCreateUpdateMixin, CreateView):
    
    @method_decorator(permission_required("menus.change_menu", _get_bookmarks))
    @method_decorator(permission_required("menus.add_link"))
    def dispatch(self, request, *args, **kwargs):
        return super(CreateBookmarkView, self).dispatch(request, *args, **kwargs)
    
class UpdateBookmarkView(BookmarkCreateUpdateMixin, UpdateView):
    
    @method_decorator(permission_required("menus.change_menu", _get_bookmarks))
    @method_decorator(permission_required("menus.change_link", _get_bookmark))
    def dispatch(self, request, *args, **kwargs):
        return super(UpdateBookmarkView, self).dispatch(request, *args, **kwargs)
        
class DeleteBookmarkView(BookmarkMixin, DeleteView):
    
    @method_decorator(permission_required("menus.change_menu", _get_bookmarks))
    @method_decorator(permission_required("menus.delete_link", _get_bookmark))
    def dispatch(self, request, *args, **kwargs):
        return super(DeleteBookmarkView, self).dispatch(request, *args, **kwargs)
