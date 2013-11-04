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

register = template.Library()

@register.simple_tag(takes_context=True)
def add_crumb(context, crumb, url=None, *args):
    """
    Add a crumb to the breadcrumb list.

    Example tag usage: {% add_crumb name [url] %}
    """
    href = url
    if url and not url.startswith('/'):
        href = reverse(url, args=args)
    if not hasattr(context['request'], "breadcrumbs"):
        context['request'].breadcrumbs = []
    context['request'].breadcrumbs.append((u'%s' % crumb, href))
    return ""

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
