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

def clean_http_referer(request, default_referer='/'):
    """Returns the HTTP referer of the given request.
    
    If the HTTP referer is not recognizable, default_referer is returned.
    """
    if not request:
        return default_referer
        
    referer = request.META.get('HTTP_REFERER', default_referer)
    
    return referer.replace("http://", "").replace("https://", "").replace(request.META['HTTP_HOST'], "")
    
def replace_path_arg(request, arg_name, arg_value):
    """Replaces arg_name's value in request with arg_value. Returns the new path.
    
    If arg_value is None, arg_name is removed from request.
    """
    path = request.META['PATH_INFO']
    path_kwargs = {}
    
    for k, v in request.GET.items():
        if not k.startswith(arg_name):
            path_kwargs.update({k: ''.join(v)})
            
    if arg_value:
        path_kwargs.update({arg_name: arg_value})
            
    path_string = ';'.join(["%s=%s" % (k, v) for k, v in path_kwargs.items()])
    if path_string:
        if path[-1] != '?':
            path += '?'
        path += path_string
        
    return path
