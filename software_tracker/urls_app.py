# -*- coding: utf-8 -*-

from __future__ import unicode_literals
# from django.conf.urls import patterns, include, url
from django.conf.urls import url
from django.views.generic import RedirectView
from software_tracker import views


urlpatterns = [

    url( r'^info/$',  views.hi, name='info_url' ),

    url( r'^apps/$', views.apps2, name='apps_url' ),

    url( r'^$',  RedirectView.as_view(pattern_name='apps_url') ),

    ]


# urlpatterns = patterns('',

#     url( r'^info/$',  'software_tracker.views.hi', name='info_url' ),

#     url( r'^apps/$', 'software_tracker.views.apps2', name='apps_url' ),

#     url( r'^$',  RedirectView.as_view(pattern_name='apps_url') ),

#     )

