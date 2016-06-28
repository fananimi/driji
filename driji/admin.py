# -*- coding: utf-8 -*-
from django.contrib import admin

from driji.models import AttendanceSummary, PhoneBook

admin.site.register(PhoneBook)
admin.site.register(AttendanceSummary)
