from django.conf.urls import url, include
from django.contrib import admin

import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^zkcluster/', include('zkcluster.urls', namespace='zkcluster')),
    url(r'^$', views.index),
    url(r'^login/$', views.login_view)
]
