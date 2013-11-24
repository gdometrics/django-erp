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

from djangoerp.core.utils.dependencies import check_dependency

check_dependency('djangoerp.core')

from django.utils.translation import ugettext_noop as _
from django.core.urlresolvers import reverse
from djangoerp.core.models import User, Group, Permission

from utils import create_detail_actions, create_detail_navigation
from models import Menu, Link

def install(sender, **kwargs):
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
    
    user_detail_actions, is_new = create_detail_actions(User)
    
    user_detail_navigation, is_new = create_detail_navigation(User)
    
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
        url="/admin/",
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
    
    user_edit_link, is_new = Link.objects.get_or_create(
        title=_("Edit"),
        slug="user-edit",
        description=_("Edit"),
        url="user_edit",
        context='{"pk": "object.pk"}',
        menu=user_detail_actions
    )
    
    user_delete_link, is_new = Link.objects.get_or_create(
        title=_("Delete"),
        slug="user-delete",
        description=_("Delete"),
        url="user_delete",
        context='{"pk": "object.pk"}',
        menu=user_detail_actions
    )
    
    # Permissions.
    users_group.permissions.add(add_bookmark)
