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
check_dependency('djangoerp.pluggets')

from django.utils.translation import ugettext_noop as _
from django.core.urlresolvers import reverse
from djangoerp.core.models import Group, Permission
from djangoerp.pluggets.models import Region, Plugget

from models import Menu, Link

def install(sender, **kwargs):
    sidebar_region, is_new = Region.objects.get_or_create(slug="sidebar")
    users_group, is_new = Group.objects.get_or_create(name="users")
    add_bookmark, is_new = Permission.objects.get_or_create_by_natural_key("add_link", "menus", "link")
    
    # Menus.
    main_menu, is_new = Menu.objects.get_or_create(
        slug="main",
        description=_("Main menu")
    )
    
    user_area_not_logged_menu, is_new = Menu.objects.get_or_create(
        slug="user_area_not_logged",
        description=_("User area for anonymous users")
    )
    
    user_area_logged_menu, is_new = Menu.objects.get_or_create(
        slug="user_area_logged",
        description=_("User area for logged users")
    )
    
    # Links.
    my_dashboard_link, is_new = Link.objects.get_or_create(
        menu=main_menu,
        title=_("My Dashboard"),
        slug="my-dashboard",
        description=_("Go back to your dashboard"),
        url="/"
    )
    
    login_link, is_new = Link.objects.get_or_create(
        title=_("Login"),
        slug="login",
        description=_("Login"),
        url=reverse("user_login"),
        only_authenticated=False,
        menu=user_area_not_logged_menu
    )
    
    administration_link, is_new = Link.objects.get_or_create(
        title=_("Administration"),
        slug="administration",
        description=_("Administration panel"),
        url="/admin",
        only_staff=True,
        menu=user_area_logged_menu
    )
    
    logout_link, is_new = Link.objects.get_or_create(
        title=_("Logout"),
        slug="logout",
        description=_("Logout"),
        url=reverse("user_logout"),
        menu=user_area_logged_menu
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
