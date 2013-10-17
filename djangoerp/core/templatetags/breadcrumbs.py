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

from django import template
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.template import Node, NodeList, Variable, Library
from django.template import TemplateSyntaxError, VariableDoesNotExist

from . import parse_args_kwargs

register = template.Library()

# Inspired by http://code.google.com/p/django-crumbs/

class AddCrumbNode(Node):
    def __init__(self, *args, **kwargs):
        self.args = [Variable(arg) for arg in args]
        self.kwargs = dict([(k, Variable(arg)) for k, arg in kwargs.items()])
        
    def render_with_args(self, context, crumb, url=None, *args):
        href = None
        if url:
            if '/' in url:
                href = url
            else:
                href = reverse(url, args=args)
        if not hasattr(context['request'], 'breadcrumbs'):
            context['request'].breadcrumbs = []
        context['request'].breadcrumbs.append((u'%s' % crumb, href))
        return ''
    
    def render(self, context):
        args = []
        for arg in self.args:
            try:
                args.append(arg.resolve(context)) 
            except VariableDoesNotExist:
                args.append(None)
        
        kwargs = {}
        for k, arg in self.kwargs.items():
            try:
                kwargs[k] = arg.resolve(context)
            except VariableDoesNotExist:
                kwargs[k] = None
        
        return self.render_with_args(context, *args, **kwargs)

@register.tag
def add_crumb(parser, token):
    """
    Add a crumb to the breadcrumb list.

    Example tag usage: {% add_crumb name [url] %}
    """
    tag_name, args, kwargs = parse_args_kwargs(parser, token)
    return AddCrumbNode(*args, **kwargs)

@register.simple_tag(takes_context=True)
def remove_last_crumb(context):
    """
    Remove the last crumb from the breadcrumb list.

    Example tag usage: {% remove_last_crumb %}
    """
    context['request'].breadcrumbs.pop()
    return ""

@register.inclusion_tag('elements/breadcrumbs.html', takes_context=True)
def render_breadcrumbs(context):
    """
    Renders the stored list of breadcrumbs.

    Example tag usage: {% render_breadcrumbs %}
    """
    try:
        breadcrumbs = context['request'].breadcrumbs
    except AttributeError:
        breadcrumbs = None
    return {'breadcrumbs': breadcrumbs}
