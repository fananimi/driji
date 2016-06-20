from django.conf.urls import url, include
from django.contrib import admin

import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^zkcluster/', include('zkcluster.urls', namespace='zkcluster')),

    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login_view),
    url(r"^logout/$", views.logout_views, name="logout"),

    url(r'^terminal/$', views.terminal, name='terminal'),
    url(r'^terminal/scan/$', views.terminal_scan, name='terminal_scan'),
    url(r'^terminal/add$', views.terminal_add, name='terminal_add'),
    url(r'^terminal/(?P<action>[\w-]+)/(?P<terminal_id>[0-9]+)/$', views.terminal_action, name='terminal_action'),

    url(r'^user/$', views.user, name='user')
]
