# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns('',

    url( r'^softare_tracker/admin/', include(admin.site.urls) ),  # eg host/project_x/admin/

    url( r'^software_tracker/', include('software_tracker.urls_app') ),  # eg host/project_x/anything/

)
