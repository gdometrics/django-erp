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

from copy import copy
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django import template
from django.template.loader import render_to_string
from django.db import models
from django import forms
from django.forms.forms import BoundField, pretty_name
from django.forms.util import flatatt
from django.contrib.contenttypes.models import ContentType
from djangoerp.core.utils.rendering import field_to_string, value_to_string

register = template.Library()

def _get_type_for_field(f):
    field_type = f.__class__.__name__.lower().replace("field", "")
    if f.choices:
        field_type += "_choices"
    return field_type
    
def _get_modelclass_from(obj):
    if isinstance(obj, models.query.QuerySet):
        return ContentType.objects.get_for_model(obj.model, False).model_class()
    try:
        return ContentType.objects.get_for_model(obj, False).model_class()
    except:
        return None
        
def _get_object_fields(form_or_model):
    field_list = []
    
    if isinstance(form_or_model, models.Model):
        field_list = dict([(f.name, f) for f in (form_or_model._meta.fields + form_or_model._meta.many_to_many)])
    elif isinstance(form_or_model, forms.Form):
        field_list = form_or_model.fields
        
    return field_list    
        
def _get_object_field(name, form_or_model):
    name, sep, suffix = name.partition(':')
    
    label = ""
    value = ""
    td_attrs = {}
    field_list = _get_object_fields(form_or_model)
    field = None
    
    if name in field_list:
        field = field_list[name]
    elif hasattr(form_or_model, name):
        field = getattr(form_or_model, name)
        if hasattr(field, 'short_description'):
            name = field.short_description

    if isinstance(field, models.Field):
        label = u'%s' % field.verbose_name
        value = field_to_string(field, form_or_model)

    elif isinstance(field, forms.Field):
        bf = BoundField(form_or_model, field, name)
        label = u'%s' % bf.label_tag()
        value = u'%s' % bf
        if bf.help_text:
            value += '<br/>\n<span class="help_text">%s</span>' % (u'%s' % bf.help_text)
        if bf._errors():
            value += '<br/>\n<ul class="errorlist">\n'
            for error in bf._errors():
                value += '\t<li>%s</li>\n' % error
            value += '</ul>\n'
        css_classes = bf.css_classes()
        if css_classes:
            td_attrs['class'] = css_classes

    else:
        name = _(pretty_name(name).lower())
        label = u'%s' % name.capitalize()
        if callable(field):
            value = value_to_string(field())
        else:
            value = value_to_string(field)

    return label, flatatt(td_attrs), mark_safe(" ".join([t for t in (value, suffix) if t]))

@register.filter
def model_name(obj):
    """Returns the model name for the given instance.

    Example usage: {{ object|model_name }}
    """
    mk = _get_modelclass_from(obj)
    if mk:
        return force_text(mk._meta.verbose_name)
    return ""

@register.filter
def model_name_plural(obj):
    """Returns the pluralized model name for the given instance.

    Example usage: {{ object|model_name_plural }}
    """
    mk = _get_modelclass_from(obj)
    if mk:
        return force_text(mk._meta.verbose_name_plural)
    return ""
    
@register.simple_tag(takes_context=True)
def render_model_list(context, object_list, field_list=[], template_name="elements/model_list.html", uid=""):
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
        
    prefix = ""
    if uid:
        prefix = "%s_" % uid
        
    model = object_list.model
    fields = [model._meta.get_field(n) for n in field_list] or model._meta.fields
    filters = dict([(f.attname, ("", "")) for f in fields])
    filters.update(context.get("%slist_filter_by" % prefix, None) or {})
    headers = [{"name": f.verbose_name, "attname": f.attname, "type": _get_type_for_field(f), "filter": {"expr": filters[f.attname][0], "value": filters[f.attname][1]}} for f in fields]
    rows = [{"object": o, "fields": [field_to_string(f, o) for f in fields]} for o in object_list]
    new_context = copy(context)
    new_context.update(
        {
            "table": {
                "uid": uid,
                "order_by": object_list.query.order_by,
                "headers": headers,
                "rows": rows
            }
        }
    )
    
    return render_to_string(template_name, new_context)

@register.simple_tag(takes_context=True)
def render_model_details(context, objects, field_layout=[], template_name="elements/model_details.html", uid=""):
    """Renders a details table from one or more model forms and/or instances.
    
    it could be also possible to specify the layout of the table, using the
    "field_layout" argument which takes a list (of lists) of field names. You
    can use it to specify not only which field goes in which row, but also if
    two or more fields should be rendered on the same row.

    Example tag usage: {% render_model_details (form|object) [(form1|object1) [...]] ["[field1, [1.field2, 2.field3], field4]"] %}
    """
    if not isinstance(objects, (list, tuple)):
        objects = [objects]
    
    if isinstance(field_layout, basestring):
        field_layout = eval(field_layout)
    elif not field_layout:
        field_layout = []
        
    def make_layout(field_list, objects):
        return_list = []
        for f in field_list:
            if isinstance(f, (tuple, list)):
                return_list.append([l[0] for l in make_layout(f, objects)])
            else:
                on, s, fn = f.rpartition('.')
                if on and fn:
                    o = objects[int(on)]
                elif not on:
                    o = objects[0]
                if o:
                    label, attrs, value = _get_object_field(fn, o)
                    return_list.append([{"name": label, "attrs": attrs, "value": value}])
        return return_list
        
    layout = make_layout(field_layout, objects)
            
    if not field_layout:
        for o in objects:
            for f in _get_object_fields(o):
                label, attrs, value = _get_object_field(f[0], o)
                layout.append([{"name": label, "attrs": attrs, "value": value}])
                
    num_cols = 1
    for row in layout:
        num_cols = max(num_cols, len(row))
                
    new_context = copy(context)
    new_context.update(
        {
            "details": {
                "uid": uid,
                "num_cols": num_cols,
                "layout": layout
            }
        }
    )
    
    return render_to_string(template_name, new_context)
            
            
        
