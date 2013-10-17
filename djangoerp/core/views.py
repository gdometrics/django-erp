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

from utils import clean_http_referer

class SetCancelUrlMixin(object):
    """Mixin that allows setting an URL to the previous logical view.
    
    It adds a context variable called "back" with the value of "cancel_url" (if
    provided) or the HTTP referer (otherwise).
    """
    cancel_url = None
    
    def get_context_data(self, **kwargs):
        context = super(SetCancelUrlMixin, self).get_context_data(**kwargs)
        context['back'] = self.request.GET.get('back', self.cancel_url or clean_http_referer(self.request))
        return context

class SetSuccessUrlMixin(object):
    """Mixin that allows setting an URL to the next logical view.
    
    It adds a context variable called "next" with the value of the "success_url"
    variable, handling automatically the "get_success_url" for forms.
    """
    success_url = None
    
    def get_context_data(self, **kwargs):
        context = super(SetSuccessUrlMixin, self).get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next', self.success_url or clean_http_referer(self.request))
        return context
        
    def get_success_url(self):
        try:
            return self.request.GET.get('next', self.success_url or clean_http_referer(self.request))
        except:
            return super(SetSuccessUrlMixin, self).get_success_url()
