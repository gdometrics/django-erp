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

from hashlib import md5
from django import template

register = template.Library()

@register.simple_tag
def avatar(email, size=36, rating='g', default=None):
    """Returns an image element with gravatar for the specified user.

    Example tag usage: {% avatar email_address 80 "g" %}
    """
    # Verify the rating actually is a rating accepted by gravatar
    rating = rating.lower()
    ratings = ['g', 'pg', 'r', 'x']
    if rating not in ratings:
        raise template.TemplateSyntaxError('rating must be %s' % (", ".join(ratings)))
        
    # Create and return the url
    h = md5(email).hexdigest()
    url = 'http://www.gravatar.com/avatar/%s?s=%s&r=%s' % (h, size, rating)
    if default:
        url = "%s&d=%s" % (url, default)
        
    return '<span class="avatar"><img width="%s" height="%s" src="%s" /></span>' % (size, size, url)

