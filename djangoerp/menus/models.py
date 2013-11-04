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

from django.db import models
from django.db.models import permalink
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
        
class Menu(models.Model):
    """Menu model.
    """
    slug = models.SlugField(max_length=100, unique=True, verbose_name=_('slug'))
    description = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('description'))

    class Meta:
        verbose_name = _('menu')
        verbose_name_plural = _('menus')

    def __unicode__(self):
        return self.description or self.slug

class Link(models.Model):
    """A generic menu entry.
    """
    menu = models.ForeignKey(Menu, related_name='links', verbose_name=_('menu'))
    title = models.CharField(max_length=100, verbose_name=_('title'))
    slug = models.SlugField(unique=True, verbose_name=_('slug'))
    url = models.CharField(max_length=200, verbose_name=_('url'))
    description = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('description'))
    new_window = models.BooleanField(default=False, verbose_name=_('New window?'))
    sort_order = models.PositiveIntegerField(default=0, verbose_name=_('sort order'))
    submenu = models.ForeignKey(Menu, db_column='submenu_id', related_name='parent_links', blank=True, null=True, verbose_name=_('sub-menu'))
    only_authenticated = models.BooleanField(default=True, verbose_name=_('Only for authenticated users'))
    only_staff = models.BooleanField(default=False, verbose_name=_('Only for staff users'))
    only_with_perms = models.ManyToManyField(Permission, blank=True, null=True, verbose_name=_('Only with following permissions'))

    class Meta:
        ordering = ('menu', 'sort_order', 'id',)
        verbose_name = _('link')
        verbose_name_plural = _('links')

    def __unicode__(self):
        return '%s | %s' % (self.menu, self.title)

    def get_absolute_url(self):
        if self.url.startswith('www.'):
            return "http://" + self.url
        return self.url

class Bookmark(Link):
    """A proxy model for bookmark links.
    """
    class Meta:
        proxy = True
        verbose_name = _('bookmark')
        verbose_name_plural = _('bookmarks')

    def __unicode__(self):
        return '%s' % self.title
        
    @models.permalink
    def get_edit_url(self):
        return ('bookmark_edit', (), {"slug": self.slug})

    @models.permalink
    def get_delete_url(self):
        return ('bookmark_delete', (), {"slug": self.slug})
