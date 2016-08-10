# -*- coding: utf-8 -*-

from django.conf.urls import include, url
from django.contrib import admin


admin.autodiscover()


urlpatterns = [

    url( r'^software/admin/', include(admin.site.urls) ),  # eg host/project_x/admin/

    url( r'^software/', include('software_tracker.urls_app') ),  # eg host/project_x/anything/

]
