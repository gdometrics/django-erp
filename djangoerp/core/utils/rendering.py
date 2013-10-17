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

from django.utils.formats import localize
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.template.defaultfilters import date, time
from django.db import models

def value_to_string(value):
    """Tries to return a smart string representation of the given value.
    """
    output = localize(value)

    if isinstance(value, (list, tuple)):
        output = ', '.join([value_to_string(v) for v in value])

    elif isinstance(value, bool):
        if value:
            output = render_to_string('elements/yes.html', {})
        else:
            output = render_to_string('elements/no.html', {})

    elif isinstance(value, float):
        output = u'%.2f' % value

    elif isinstance(value, int):
        output = '%d' % value

    if not value and not output:
        output = render_to_string('elements/empty.html', {})

    return mark_safe(output)


def field_to_value(field, instance):
    """Tries to convert a model field value in something smarter to render.
    """
    value = getattr(instance, field.name)

    if field.primary_key or isinstance(field, (models.SlugField, models.PositiveIntegerField)):
        if value:
          return u'#%d' % value

    elif isinstance(field, (models.ForeignKey, models.OneToOneField)):
        try:
            return render_to_string('elements/link.html', {'url': value.get_absolute_url(), 'caption': value})
        except AttributeError:
            return value

    elif isinstance(field, models.ManyToManyField):
        items = []
        for item in value.all():
            try:
                items.append(render_to_string('elements/link.html', {'url': item.get_absolute_url(), 'caption': item}))
            except AttributeError:
                items.append(u'%s' % item)
        return items

    elif isinstance(field, models.DateTimeField):
        return date(value, settings.DATETIME_FORMAT)

    elif isinstance(field, models.DateField):
        return date(value, settings.DATE_FORMAT)

    elif isinstance(field, models.TimeField):
        return time(value, settings.TIME_FORMAT)

    elif isinstance(field, models.URLField) and value:
        return render_to_string('elements/link.html', {'url': value, 'caption': value})

    elif isinstance(field, models.EmailField) and value:
        return render_to_string('elements/link.html', {'url': 'mailto:%s' % value, 'caption': value})

    elif field.choices:
        return getattr(instance, 'get_%s_display' % field.name)()

    elif isinstance(field, models.BooleanField):
        if value == '0' or not value:
            return False
        return True

    return value


def field_to_string(field, instance):
    """All-in-one conversion from a model field value to a smart string representation.
    """
    return value_to_string(field_to_value(field, instance))
