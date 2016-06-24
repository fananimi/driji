# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from importlib import import_module

from django.apps import AppConfig


class DrijiConfig(AppConfig):
    name = 'driji'
    verbose_name = 'driji'

    def ready(self):
        import_module('driji.signals')
