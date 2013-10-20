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

from django.db.models.signals import post_save
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType

from cache import LoggedInUserCache
from models import ObjectPermission

## HANDLERS ##

def _update_author_permissions(sender, instance, *args, **kwargs):
    """Updates the permissions assigned to the author of the given object.
    """
    author = LoggedInUserCache().current_user
    content_type = ContentType.objects.get_for_model(sender)
    app_label = content_type.app_label
    model_name = content_type.model

    if author:
        print "Creating perms of %s for %s" % (author, instance)
        
        can_view_this_object, is_new = ObjectPermission.objects.get_or_create_by_natural_key("view_%s" % model_name, app_label, model_name, instance.pk)
        can_change_this_object, is_new = ObjectPermission.objects.get_or_create_by_natural_key("change_%s" % model_name, app_label, model_name, instance.pk)
        can_delete_this_object, is_new = ObjectPermission.objects.get_or_create_by_natural_key("delete_%s" % model_name, app_label, model_name, instance.pk)

        can_view_this_object.users.add(author)
        can_change_this_object.users.add(author)
        can_delete_this_object.users.add(author)
        
def manage_author_permissions(cls):
    """Adds permissions assigned to the author of the given object.
    
    Connects the post_save signal of the given model class to the handler which
    adds default permissions to the current user. i.e.:
    
    >> manage_author_permissions(Project)
    
    It will add default view, change and delete permissions for each Project's
    instances created by the current user.
    """
    post_save.connect(_update_author_permissions, cls, dispatch_uid="update_%s_permissions" % cls)
    

## CONNECTIONS ##

manage_author_permissions(Comment)
