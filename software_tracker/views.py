# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import datetime, json, logging, os, pprint
from django.conf import settings as project_settings
from django.contrib.auth import logout
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from software_tracker import models

log = logging.getLogger(__name__)


def hi( request ):
    """ Returns simplest response. """
    now = datetime.datetime.now()
    return HttpResponse( '<p>hi</p> <p>( %s )</p>' % now )


def apps2( request ):
    """Preps data; returns main display page or json."""  # TODO: a) delete base.html; b) cache
    return HttpResponse( 'coming' )
    ## prep data
    url_scheme, url_server = request.META[u'wsgi.url_scheme'], request.META[u'SERVER_NAME']
    api_list, production_list, current_development_list = [], [], []
    for obj in models.Software.objects.filter( api=True ):
        api_list.append( obj.make_serializable_dict( url_scheme, url_server ) )
    for obj in models.Software.objects.filter( in_production=True ):
        production_list.append( obj.make_serializable_dict( url_scheme, url_server ) )
    for obj in models.Software.objects.filter( current_development=True ):
        current_development_list.append( obj.make_serializable_dict( url_scheme, url_server ) )
    data_dict = {
        u'api_list': api_list,
        u'production_list': production_list,
        u'current_development_list': current_development_list,
        }
    ## display
    format = request.GET.get( u'format', None )
    callback = request.GET.get( u'callback', None )
    if format == u'json':
        d = { u'datetime': u'%s' % datetime.datetime.now(), u'message': u'format=json called', u'remote_ip': u'%s' % request.META[u'REMOTE_ADDR'] }
        log.info( json.dumps(d, sort_keys=True) )
        output = json.dumps( data_dict, sort_keys=True, indent=2 )
        if callback:
              output = u'%s(%s)' % ( callback, output )
        return HttpResponse( output, content_type = u'application/javascript; charset=utf-8' )
    else:
        data_dict[u'LOGIN_URL'] = settings_app.LOGIN_URL
        return render( request, u'software_app_templates/base2.html', data_dict )

# def apps2( request ):
#     """Preps data; returns main display page or json."""  # TODO: a) delete base.html; b) cache
#     ## prep data
#     url_scheme, url_server = request.META[u'wsgi.url_scheme'], request.META[u'SERVER_NAME']
#     api_list, production_list, current_development_list = [], [], []
#     for obj in models.Software.objects.filter( api=True ):
#     api_list.append( obj.make_serializable_dict( url_scheme, url_server ) )
#     for obj in models.Software.objects.filter( in_production=True ):
#     production_list.append( obj.make_serializable_dict( url_scheme, url_server ) )
#     for obj in models.Software.objects.filter( current_development=True ):
#     current_development_list.append( obj.make_serializable_dict( url_scheme, url_server ) )
#     data_dict = {
#         u'api_list': api_list,
#         u'production_list': production_list,
#         u'current_development_list': current_development_list,
#         }
#     ## display
#     format = request.GET.get( u'format', None )
#     callback = request.GET.get( u'callback', None )
#     if format == u'json':
#         d = { u'datetime': u'%s' % datetime.datetime.now(), u'message': u'format=json called', u'remote_ip': u'%s' % request.META[u'REMOTE_ADDR'] }
#         log.info( json.dumps(d, sort_keys=True) )
#         output = json.dumps( data_dict, sort_keys=True, indent=2 )
#         if callback:
#               output = u'%s(%s)' % ( callback, output )
#         return HttpResponse( output, content_type = u'application/javascript; charset=utf-8' )
#     else:
#         data_dict[u'LOGIN_URL'] = settings_app.LOGIN_URL
#         return render( request, u'software_app_templates/base2.html', data_dict )
