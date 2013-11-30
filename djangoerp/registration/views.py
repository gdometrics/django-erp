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

import datetime

from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings

from models import *
from forms import *

def user_register(request):
    """Registers a new user account.
    """
    if request.user.is_authenticated():
        messages.info(request, _("You are already registered."))
        return redirect("/")

    user = get_user_model()(is_active=False)
        
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, _("An email has been sent with an activation key. Please check your mail to complete the registration."))
            return redirect("/")
    else:
        form = UserRegistrationForm(instance=user)

    return render_to_response('registration/register.html', RequestContext(request, {'form': form}))        
    
def user_activate(request, activation_key):
    """Activates a pending user account.
    """
    token = get_object_or_404(ActivationToken, activation_key=activation_key)
    user_account = token.user
    if user_account.is_active:
        messages.info(request, _("This account is already active."))
        if request.user.is_authenticated():
            return redirect("/")
        return redirect(reverse('user_login'))
    try:
        if token.key_expiration < datetime.datetime.today():
            messages.error(request, _("Sorry, your account is expired."))
            return redirect("/")
    except TypeError:
        pass
    user_account.is_active = True
    user_account.save()
    messages.success(request, _("Congratulations! Your account is now active."))
    token.delete()
    return redirect(reverse('user_login'))
