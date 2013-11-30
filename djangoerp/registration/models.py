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

from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.conf import settings

class ActivationToken(models.Model):
    """Activation token for user account.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, verbose_name=_("user"))
    activation_key = models.CharField(_("activation key"), max_length=40, blank=True, null=True)
    key_expiration = models.DateTimeField(_("key expiration"), blank=True, null=True)
    
    class Meta:
        verbose_name = _('activation token')
        verbose_name_plural = _('activation tokens')
