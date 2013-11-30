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
check_dependency('djangoerp.menus')

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_noop as _

from djangoerp.menus.models import Menu, Link

def install(sender, **kwargs):
    user_area_not_logged_menu, is_new = Menu.objects.get_or_create(slug="user_area_not_logged")
    
    # Links.
    register_link, is_new = Link.objects.get_or_create(
        title=_("Register"),
        slug="register",
        description=_("Register a new account"),
        url=reverse("user_register"),
        only_authenticated=False,
        menu=user_area_not_logged_menu
    )
