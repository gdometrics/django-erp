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

import urlparse
from functools import wraps
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils.decorators import available_attrs

def obj_permission_required(perm, get_obj_func=None, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """Checks if the user has "perm" for obj returned by "get_obj_func".

    It first checks if the user has generic model permissions. If no model
    permissions are found, the decorator checks if the user has permissions
    specific for the obj returned invoking "get_obj_func" with the arguments
    of the decorated view function.

    Also "perm" could be a function which returns a permission name (invoked
    passing the arguments of the decorated view).
    """
    def decorator(viewfunc):
        @wraps(viewfunc, assigned=available_attrs(viewfunc))
        def _wrapped_view(request, *args, **kwargs):
            obj = None
            perm_name = perm
            if callable(perm):
                perm_name = perm(request, *args, **kwargs)
            if callable(get_obj_func):
                obj = get_obj_func(request, *args, **kwargs)
            if request.user.has_perm(perm_name, obj):
                return viewfunc(request, *args, **kwargs)
            if request.user.has_perm(perm_name):
                return viewfunc(request, *args, **kwargs)
            path = request.build_absolute_uri()
            # If the login url is the same scheme and net location then just
            # use the path as the "next" url.
            login_scheme, login_netloc = urlparse.urlparse(login_url or settings.LOGIN_URL)[:2]
            current_scheme, current_netloc = urlparse.urlparse(path)[:2]
            if ((not login_scheme or login_scheme == current_scheme) and
                (not login_netloc or login_netloc == current_netloc)):
                path = request.get_full_path()
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(path, login_url, redirect_field_name)
        return _wrapped_view
    return decorator
