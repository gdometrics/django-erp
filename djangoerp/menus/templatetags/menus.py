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
from django import template
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model

from ..models import Menu

register = template.Library()

DEFAULT_MENU_TEMPLATE = "menus/menu.html"

def _render_menu(slug, context, html_template=DEFAULT_MENU_TEMPLATE):
    """Helpers function which takes a menu slug, a context and a template and
    renders the given menu using the given template with the given context.
    """
    try:
        menu = Menu.objects.get(slug=slug)
        user = context['user']
        links = menu.links.all()
        for link in links:
            perms = ["%s.%s" % (p.content_type.app_label, p.codename) for p in link.only_with_perms.all()]
            link.authorized = True
            link.title = template.Template(link.title).render(context)
            if link.description:
                link.description = template.Template(link.description).render(context)
            link.url = template.Template(link.url).render(context)
            if not (user.is_staff or user.is_superuser):
                if link.only_authenticated and not user.is_authenticated():
                    link.authorized = False
                elif link.only_staff and not (user.is_staff or user.is_superuser):
                    link.authorized = False
                elif link.only_with_perms:
                    link.authorized = user.has_perms(perms)
    except Menu.DoesNotExist:
        links = None
    html_template = ("%s" % html_template).replace('"', '').replace("'", "")
    if links:
        return render_to_string(html_template, {'slug': slug, 'links': links}, context)
    return ""
    

class MenuNode(template.Node):
    def __init__(self, slug, html_template=DEFAULT_MENU_TEMPLATE):
        self.slug = slug
        self.html_template = html_template

    def render(self, context):
        output = ''
        slug = self.slug.resolve(context)
        html_template = self.html_template
        if isinstance(self.html_template, template.Variable):
            html_template = self.html_template.resolve(context)
        return _render_menu(slug, context, html_template)

@register.tag
def menu(parser, token):
    """
    Renders a menu.

    Example tag usage: {% menu menu_slug [html_template] %}
    """
    try:
        args = token.split_contents()
        if len(args) < 2:
            raise ValueError
        elif len(args) == 2:
            slug = parser.compile_filter(args[1])
            html_template = 'menus/menu.html'
        else:
            slug = parser.compile_filter(args[1])
            html_template = parser.compile_filter(args[2])
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires one or two arguments" % token.contents.split()[0]

    return MenuNode(slug, html_template)
    
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
                url = template.Template(l.url).render(context)
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
