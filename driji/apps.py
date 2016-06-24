# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from importlib import import_module


class DrijiConfig(AppConfig):
    name = 'driji'
    verbose_name = 'driji'

    def ready(self):
        import_module('driji.signals')
