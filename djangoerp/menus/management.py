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

from djangoerp.core.utils.dependencies import check_dependency

check_dependency('djangoerp.core')
check_dependency('djangoerp.authtools')
check_dependency('djangoerp.pluggets')

from django.utils.translation import ugettext_noop as _
from djangoerp.authtools.models import Group, Permission
from djangoerp.pluggets.models import Region, Plugget

from models import Menu, Link

def install(sender, **kwargs):
    sidebar_region, is_new = Region.objects.get_or_create(slug="sidebar")
    users_group, is_new = Group.objects.get_or_create(name="users")
    add_bookmark, is_new = Permission.objects.get_or_create_by_natural_key("add_bookmark", "menus", "bookmark")
    
    # Menus.
    main_menu, is_new = Menu.objects.get_or_create(
        slug="main",
        description=_("Main menu")
    )
    
    # Links.
    my_dashboard_link, is_new = Link.objects.get_or_create(
        menu=main_menu,
        title=_("My Dashboard"),
        slug="my-dashboard",
        description=_("Go back to your dashboard"),
        url="/"
    )
    
    # Pluggets.
    main_menu_plugget, is_new = Plugget.objects.get_or_create(
        title=_("Main menu"),
        source="djangoerp.menus.pluggets.menu",
        template="menus/pluggets/menu.html",
        context='{"name": "main"}',
        sort_order=1,
        region=sidebar_region
    )
    
    # Permissions.
    users_group.permissions.add(add_bookmark)
