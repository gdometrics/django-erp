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

from django.test import TestCase

from ..models import *

class JSONValidationCase(TestCase):
    def test_correct_json_validation(self):
        """Tests that when a JSON snippet is incorrect, an error must be raised.
        """
        try:
          validate_json('{"id":1,"name":"foo","interest":["django","django ERP"]}')
          self.assertTrue(True)
        except ValidationError:
          self.assertFalse(True)
          
    def test_incorrect_json_validation(self):
        """Tests that when a JSON snippet is incorrect, an error must be raised.
        """
        try:
          # The snippet is incorrect due to the double closed square bracket.
          validate_json('{"id":1,"name":"foo","interest":["django","django ERP"]]}')
          self.assertFalse(True)
        except ValidationError:
          self.assertTrue(True)
