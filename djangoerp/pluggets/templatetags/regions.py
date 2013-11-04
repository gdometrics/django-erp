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
        
@register.simple_tag(takes_context=True)
def render_plugget(context, plugget_pk, template_name=None):
    """Renders the plugget identified by the given ID with the given template.
    
    It takes the following arguments:
    
     * plugget_pk -- Univoque ID which identifies the plugget that should be
                     rendered.
     * template_name -- Template to be used to render the plugget. If empty, the
                        specific plugget's template will be used.
                        [default: None] 
    
    Example usage: {% render_plugget plugget_pk template_name %}
    """    
    context = copy(context)
    
    if isinstance(plugget_pk, template.Variable):
        plugget_pk = plugget_pk.resolve(context)
    if isinstance(template_name, template.Variable):
        template_name = template_name.resolve(context)
    
    try:
        plugget = Plugget.objects.get(pk=plugget_pk)
        if plugget.context:
            context.update(json.loads(plugget.context))
        pkg, sep, name = plugget.source.rpartition('.')
        try:
            m = __import__(pkg, {}, {}, [name])
            func = getattr(m, name)
            context = func(context)
        except:
            pass
        return render_to_string(template_name or plugget.template, {'plugget': plugget}, context)
            
    except ObjectDoesNotExist:
        pass
        
    return ""    

@register.simple_tag(takes_context=True)
def render_region(context, region_slug, template_name="pluggets/region.html"):
    """Renders the region identified by the given slug with the given template.
    
    It takes the following arguments:
    
     * region_slug -- Univoque slug which identifies the region that should be
                      rendered.
     * template_name -- Template to be used to render the region.
                        [default: pluggets/region.html] 
    
    Example usage: {% render_region region_slug template_name %}
    """    
    if isinstance(region_slug, template.Variable):
        region_slug = region_slug.resolve(context)
    if isinstance(template_name, template.Variable):
        template_name = template_name.resolve(context)
    
    try:
        region = Region.objects.get(slug=region_slug)
        context['region'] = region
        
        return render_to_string(template_name, context)
        
    except ObjectDoesNotExist:
        pass
        
    return ""
    
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
