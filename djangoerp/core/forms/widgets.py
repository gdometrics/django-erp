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

import json
from django import forms
from django.forms.widgets import flatatt
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

class JsonPairWidget(forms.Widget):
    """A widget that displays a list of text key/value pairs.

    key_attrs -- html attributes applied to the 1st input box pairs
    val_attrs -- html attributes applied to the 2nd input box pairs

    Inspired by:

    http://www.huyng.com/archives/django-custom-form-widget-for-dictionary-and-tuple-key-value-pairs/
    """
    def __init__(self, *args, **kwargs):
        key_attrs = {}
        val_attrs = {}
        if "key_attrs" in kwargs:
            key_attrs = kwargs.pop("key_attrs")
        if "val_attrs" in kwargs:
            val_attrs = kwargs.pop("val_attrs")
        if "class" not in key_attrs:
            key_attrs['class'] = ''
        if "class" not in val_attrs:
            val_attrs['class'] = ''
        key_attrs['class'] = ' '.join(['json-key', key_attrs['class']]) 
        val_attrs['class'] = ' '.join(['json-val', val_attrs['class']]) 
        self.attrs = {'key_attrs': key_attrs, 'val_attrs': val_attrs}
        super(forms.Widget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        try:
            data = json.loads(force_unicode(value))
        except:
            data = {}

        output = ''
        for k,v in data.items():
            output += self.render_pair(k, v, name)
        output += self.render_pair('', '', name)

        return mark_safe(output)

    def render_pair(self, key, value, name):
        ctx = {
            'key': key,
            'value': value,
            'fieldname': name,
            'key_attrs': flatatt(self.attrs['key_attrs']),
            'val_attrs': flatatt(self.attrs['val_attrs'])
        }
        return '<input type="text" name="json_key[%(fieldname)s]" value="%(key)s" %(key_attrs)s> <input type="text" name="json_value[%(fieldname)s]" value="%(value)s" %(val_attrs)s><br />' % ctx

    def value_from_datadict(self, data, files, name):
        jsontext = ""
        if data.has_key('json_key[%s]' % name) and data.has_key('json_value[%s]' % name):
            keys     = data.getlist("json_key[%s]" % name)
            values   = data.getlist("json_value[%s]" % name)
            data = {}
            for key, value in zip(keys, values):
                if len(key) > 0:
                    data[key] = value
            jsontext = json.dumps(data)
        return jsontext
