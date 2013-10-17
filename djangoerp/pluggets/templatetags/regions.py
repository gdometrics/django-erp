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

import re
import json
from copy import copy
from django import template
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType

from ..models import Region, Plugget

register = template.Library()

class PluggetNode(template.Node):
    def __init__(self, plugget_pk, template=None):
        self.template = template
        self.plugget_pk = plugget_pk

    def render(self, context):
        output = ''
        context = copy(context)
        
        try:
            plugget = Plugget.objects.get(pk=self.plugget_pk)
            if self.template is None:
                self.template = plugget.template
            if plugget.context:
                context.update(json.loads(plugget.context))
            pkg, sep, name = plugget.source.rpartition('.')
            try:
                m = __import__(pkg, {}, {}, [name])
                func = getattr(m, name)
                context = func(context)
            except:
                pass
            output += render_to_string(self.template, {'plugget': plugget}, context)
                
        except ObjectDoesNotExist:
            pass
            
        return output

class RegionNode(template.Node):
    def __init__(self, slug):
        self.slug = slug

    def render(self, context):
        output = ''
        slug = self.slug.resolve(context)
        
        try:
            region = Region.objects.get(slug=slug)
            pluggets = region.pluggets.all()
            output += '<div class="region" id="%s-region">\n' % region.slug
            for index, plugget in enumerate(pluggets):
                context['plugget_index'] = index
                output += PluggetNode(plugget.pk).render(context)
            output += '</div>\n'
            
        except ObjectDoesNotExist:
            pass
            
        return output

@register.tag
def region(parser, token):
    """Renders the region identified by the given slug.
    
    Example usage: {% region region_slug %}
    """
    region_name = None
    
    try:
        args = token.split_contents()
        if len(args) == 2:
            region_name = parser.compile_filter(args[1])
        else:
            raise ValueError
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents.split()[0]

    return RegionNode(region_name)
    
@register.assignment_tag
def regions_for(obj):
    """Returns all the regions related to the given obj in a context variable.
    
    Example usage: {% region_for obj as obj_regions %}
    """
    try:
        return Region.objects.filter(content_type=ContentType.objects.get_for_model(obj), object_id=obj.pk)
    except:
        return []
    
@register.assignment_tag
def first_region_for(obj):
    """Returns the first region related to the given obj in a context variable.
    
    Example usage: {% first_region_for obj as obj_first_region %}
    """
    try:
        return Region.objects.get(content_type=ContentType.objects.get_for_model(obj), object_id=obj.pk)
    except:
        return None
