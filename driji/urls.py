# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from django.contrib import admin

import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^i18n/', include('django.conf.urls.i18n')),

    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login_view),
    url(r"^logout/$", views.logout_views, name="logout"),

    url(r'^terminal/$', views.terminal, name='terminal'),
    url(r'^terminal/scan/$', views.terminal_scan, name='terminal_scan'),
    url(r'^terminal/add$', views.terminal_add, name='terminal_add'),
    url(r'^terminal/(?P<terminal_id>[0-9]+)/$', views.terminal_detail, name='terminal_detail'),
    url(r'^terminal/(?P<action>[\w-]+)/(?P<terminal_id>[0-9]+)/$', views.terminal_action, name='terminal_action'),

    url(r'^student/$', views.student, name='student'),
    url(r'^student/add/$', views.student_add, name='student_add'),

    url(r'^attendance/(?P<terminal_id>[0-9]+)/$$', views.attendance, name='attendance'),

    url(r'^sms/$', views.sms, name='sms'),

    url(r'^settings/grade/$', views.index, name='settings_grade'),
    url(r'^settings/grade/add/$', views.index, name='settings_grade_add')
]
