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
from django.template.loader import render_to_string
from django.db import models
from django.contrib.contenttypes.models import ContentType
from djangoerp.core.utils.rendering import field_to_string

register = template.Library()

def _get_type_for_field(f):
    field_type = f.__class__.__name__.lower().replace("field", "")
    if f.choices:
        field_type += "_choices"
    return field_type
    
def _get_modelclass_from(obj):
    if isinstance(obj, models.query.QuerySet):
        return ContentType.objects.get_for_model(obj.model).model_class()
    try:
        return ContentType.objects.get_for_model(obj).model_class()
    except:
        return None

@register.filter
def model_name(obj):
    """Returns the model name for the given instance.

    Example usage: {{ object|model_name }}
    """
    mk = _get_modelclass_from(obj)
    if mk:
        return mk._meta.verbose_name
    return ""

@register.filter
def model_name_plural(obj):
    """Returns the pluralized model name for the given instance.

    Example usage: {{ object|model_name_plural }}
    """
    mk = _get_modelclass_from(obj)
    if mk:
        return mk._meta.verbose_name_plural
    return ""
    
@register.simple_tag
def render_model_list(object_list, field_list=[], template_name="elements/model_list.html", uid=""):
    """Renders a table with given fields for all given model instances.
    
    It takes three optional arguments:
    
     * field_list -- The list of field names to be rendered [default: all].
     * template_name -- Template that renders the list [default: elements/table_list.html]
     * uid -- An universal ID for this model list (must be unique in the template context).

    Example tag usage: {% render_model_list object_list [fields] [template_name] %}
    """
    if not isinstance(object_list, models.query.QuerySet):
        return ""
        
    if not field_list:
        field_list = []
        
    model = object_list.model
    fields = [model._meta.get_field(n) for n in field_list] or model._meta.fields
    headers = [{"name": f.verbose_name, "type": _get_type_for_field(f)} for f in fields]
    rows = [{"object": o, "fields": [field_to_string(f, o) for f in fields]} for o in object_list]
    
    return render_to_string(
        template_name,
        {
            "table": {
                "uid": uid,
                "headers": headers,
                "rows": rows
            }
        }
    )

@register.simple_tag
def render_model_properties(parser, token):
    """Renders a property table from one or more model forms and/or instances.
    
    it could be also possible to specify the layout of the table, using the last
    argument which takes a list (of lists) of field names. You can use it to
    specify not only which field goes in which row, but also if two or more
    fields should be rendered on the same row.

    Example tag usage: {% render_model_properties (form|object) [(form1|object1) [...]] ["[field1, [field2, field3], field4]"] %}
    """
    return ""
