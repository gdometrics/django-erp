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
from django import template
from django.core.urlresolvers import reverse, NoReverseMatch
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model

from ..models import Menu

register = template.Library()

DEFAULT_MENU_TEMPLATE = "menus/menu.html"

def _calculate_link_params(link, context):
    """Helper function which takes a Link instance and a context and calculates
    the final values of its params (i.e. URL, title, description, etc.)
    """
    user = context['user']
    link_context = dict([(k, template.Variable(v).resolve(context)) for k, v in json.loads(link.context or "{}").items()])
    link.title = link.title % link_context
    if link.description:
        link.description = link.description % link_context
    try:
        link.url = reverse(link.url, args=[], kwargs=link_context, current_app=context.current_app)
    except NoReverseMatch:
        pass
    perms = ["%s.%s" % (p.content_type.app_label, p.codename) for p in link.only_with_perms.all()]
    link.authorized = True
    if not (user.is_staff or user.is_superuser):
        if link.only_authenticated and not user.is_authenticated():
            link.authorized = False
        elif link.only_staff and not (user.is_staff or user.is_superuser):
            link.authorized = False
        elif link.only_with_perms:
            link.authorized = user.has_perms(perms, link_context.get("object", None))
    return link
    

def _render_menu(slug, context, html_template=DEFAULT_MENU_TEMPLATE):
    """Helper function which takes a menu slug, a context and a template and
    renders the given menu using the given template with the given context.
    """
    links = None
    try:
        if isinstance(slug, template.Variable):
            slug = slug.resolve(context)
        if isinstance(html_template, template.Variable):
           html_template = html_template.resolve(context)
        menu = Menu.objects.get(slug=slug)
        links = menu.links.all()
        for link in links:
            _calculate_link_params(link, context)
    except Menu.DoesNotExist:
        pass
    html_template = ("%s" % html_template).replace('"', '').replace("'", "")
    if links:
        return render_to_string(html_template, {'slug': slug, 'links': links}, context)
    return ""

@register.simple_tag(takes_context=True)
def render_menu(context, slug, html_template=DEFAULT_MENU_TEMPLATE):
    """Renders a menu.

    Example tag usage: {% render_menu menu_slug [html_template] %}
    """
    return _render_menu(slug, context, html_template)
    
@register.simple_tag(takes_context=True)
def render_user_bookmarks(context):
    """Renders the bookmark menu for the current logged user.
    
    Example tag usage: {% render_user_bookmarks %}
    """
    user = context['user']
    if isinstance(user, get_user_model()) and user.pk:
        return _render_menu("user_%d_bookmarks" % user.pk, context)
    return ""    

@register.assignment_tag(takes_context=True)
def score_link(context, link, ref_url, css_class="active"):
    """Checks if the link instance is the best match for "ref_url".

    Example tag usage: {% score_link link ref_url [css_class] as class %}
    """
    def best_match(menu, parent=None, score=len(ref_url), matched_link=None):
        if menu:
            for l in menu.links.all():
                l = _calculate_link_params(l, context)
                url = l.url
                if url == ref_url or ref_url.startswith(url):
                    remainder = ref_url[len(url):]
                    current_score = len(remainder)
                    if current_score < score:
                        score = current_score
                        matched_link = parent or l
                        continue
                score, matched_link = best_match(l.submenu, parent or l, score, matched_link)
        return score, matched_link
    score, matched_link = best_match(link.menu)                              
    if matched_link == link:
        return css_class
    return ""
