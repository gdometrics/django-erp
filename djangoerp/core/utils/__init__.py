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

def get_model(klass):
    """Tries to return the model class identified by klass.
    
    If klass is already a model class, is returned as it is.
    If klass is a model instance or queryset, its model class is returned.
    If klass is a string, it's used to retrieve the related real model class.
    
    A ValueError is raised on other cases.
    """
    from django.db import models
    
    try:
        if issubclass(klass, models.Model):
            return klass
    except:
        pass
        
    if isinstance(klass, models.Model):
        return klass.__class__
        
    elif isinstance(klass, models.query.QuerySet):
        return klass.model
        
    elif isinstance(klass, basestring):
        app_label, sep, model_name = klass.rpartition('.')
        return models.get_model(app_label, model_name)
        
    raise ValueError

def clean_http_referer(request, default_referer='/'):
    """Returns the HTTP referer of the given request.
    
    If the HTTP referer is not recognizable, default_referer is returned.
    """
    if not request:
        return default_referer
        
    referer = request.META.get('HTTP_REFERER', default_referer)
    
    return referer.replace("http://", "").replace("https://", "").replace(request.META['HTTP_HOST'], "")
    
def set_path_kwargs(request, **kwargs):
    """Adds/sets the given kwargs to request path and returns the result.
    
    If a kwarg's value is None, it will be removed from path.
    """
    path = request.META['PATH_INFO']
    path_kwargs = {}
    
    for k, v in request.GET.items():
        if not k in kwargs:
            path_kwargs.update({k: ''.join(v)})
            
    path_kwargs.update(kwargs)
            
    path_kwargs_string = ';'.join(["%s=%s" % (k, v) for k, v in path_kwargs.items() if v])
    if path_kwargs_string:
        if path[-1] != '?':
            path += '?'
        path += path_kwargs_string
        
    return path
