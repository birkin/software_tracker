# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import datetime, json, logging, os, pprint
from django.conf import settings as project_settings
# from django.core.urlresolvers import reverse
from django.urls import reverse
from django.db import models
from django.http import HttpResponseRedirect
from django.utils.encoding import smart_unicode

log = logging.getLogger(__name__)


### db models ###


class Software(models.Model):
  ACTIVITY_CHOICES = (
    ( '4', 'high' ),  # ('value-in-db', 'value-displayed')
    ( '3', 'medium' ),
    ( '2', 'low' ),
    ( '1', 'archived' ),
    )
  AUDIENCE_CHOICES = (
    ( 'public', 'public' ),
    ( 'staff', 'staff' ),
    )
  name = models.CharField( max_length=100 )
  slug = models.SlugField()
  description = models.TextField( blank=True, help_text='plain text, or markdown syntax (http://daringfireball.net/projects/markdown/)' )
  # description_is_markdown = models.BooleanField( default=False )
  composed_of = models.ManyToManyField( 'self', blank=True, related_name='components', symmetrical=False )
  url_interactive = models.URLField( blank=True )
  url_source = models.URLField( blank=True )
  url_documentation = models.URLField( blank=True )
  url_license = models.URLField( blank=True )
  license_name = models.CharField( max_length=100, blank=True )
  contact_domain_name = models.CharField( max_length=100, blank=True )
  contact_domain_email = models.EmailField( blank=True )
  contact_technical_name = models.CharField( max_length=100, blank=True )
  contact_technical_email = models.EmailField( blank=True )
  url_feedback = models.URLField( blank=True )
  urls_pub_relations = models.TextField( blank=True, help_text='must be valid json list of dicts, like [ {"date": "x", "label": "y", "url": "z"} ]' )
  urls_presentations = models.TextField( blank=True, help_text='format: { "label": "url" }' )
  in_production = models.BooleanField( default=False )
  api = models.BooleanField( default=False )
  current_development = models.BooleanField( default=False )
  activity = models.CharField( max_length=20, blank=True, choices=ACTIVITY_CHOICES )
  audience = models.CharField( max_length=20, blank=True, choices=AUDIENCE_CHOICES )

  def __unicode__(self):
    return smart_unicode( self.name, u'utf-8', u'replace' )

  def save(self):
    ## urls_pub_relations check
    if len( self.urls_pub_relations.strip() ) == 0:
      super(Software, self).save()
    else:
      try:
        li = json.loads( self.urls_pub_relations )
        self.urls_pub_relations = json.dumps( li, indent=2, sort_keys=True )
        super(Software, self).save()
      except:
        raise Exception( u'Problem with "urls_pub_relations" field; valid json required; previous info remains; hit back button to correct.' )

  def _getHighlight(self):
    '''grabs first dict in list if it exists'''
    try:
      li = json.loads( self.urls_pub_relations )
      return li[0]
    except:
      return None
  highlight = property( _getHighlight )

  class Meta:
    ordering = [ u'name' ]
    verbose_name_plural = u'Software'

  def make_serializable_dict( self, url_scheme, url_server ):
    """Converts attribute and other info into dict and returns it; dict will either be passed to template or exposed as json."""
    import django  # for asserts
    dic = {}
    ## most attributes
    for key,value in self.__dict__.items():
      if key == u'_state':                  # not a real attribute, and not serializable
        continue
      elif key == u'id':                    # unnecessary
        continue
      elif key == u'activity' and value:
        dic[key] = dict(self.ACTIVITY_CHOICES)[value]
      elif key == u'audience' and value:
        dic[key] = dict(self.AUDIENCE_CHOICES)[value]
      else:
        dic[key] = value
    ## 'composed of' attribute (not in __dict__)
    composed_of_list = []
    composed_of_queryset = self.composed_of.values()
    log.debug( 'composed_of_queryset, `{}`'.format(composed_of_queryset) )
    log.debug( 'type(composed_of_queryset), `{}`'.format(type(composed_of_queryset)) )
    # assert type(composed_of_queryset) == django.db.models.query.ValuesQuerySet  # not serializable (original code)
    assert type(composed_of_queryset) == django.db.models.query.QuerySet  # updated due to error on above
    for dict_entry in composed_of_queryset:
      sub_dict = { u'name': dict_entry[u'name'] }
      sub_dict[u'url_software_page'] = u'%s://%s%s#%s' % ( url_scheme, url_server, reverse(u'apps_url',), dict_entry[u'slug'] )
      composed_of_list.append( sub_dict )   # for reference: quick way to get all standard attributes: composed_of_list.append( dict_entry )
    dic[u'composed_of'] = composed_of_list
    ## 'highlight' attribute                # non-standard 'property' attribute
    dic[u'highlight'] = self.highlight
    ## non-attribute info
    dic[u'url_software_page'] = u'%s://%s%s#%s' % ( url_scheme, url_server, reverse(u'apps_url',), self.slug )
    ## return
    return dic

  # def make_serializable_dict( self, url_scheme, url_server ):
  #   """Converts attribute and other info into dict and returns it; dict will either be passed to template or exposed as json."""
  #   import django  # for asserts
  #   dic = {}
  #   ## most attributes
  #   for key,value in self.__dict__.items():
  #     if key == u'_state':                # not a real attribute, and not serializable
  #       continue
  #     elif key == u'activity' and value:
  #       dic[key] = dict(self.ACTIVITY_CHOICES)[value]
  #     elif key == u'audience' and value:
  #       dic[key] = dict(self.AUDIENCE_CHOICES)[value]
  #     else:
  #       dic[key] = value
  #   ## 'composed of' attribute (not in __dict__)
  #   composed_of_list = []
  #   composed_of_queryset = self.composed_of.values()
  #   assert type(composed_of_queryset) == django.db.models.query.ValuesQuerySet  # not serializable
  #   for dict_entry in composed_of_queryset:
  #     dict_entry[u'url_software_page'] = u'%s://%s%s#%s' % ( url_scheme, url_server, reverse(u'apps_url',), dict_entry[u'slug'] )
  #     composed_of_list.append( dict_entry )
  #   dic[u'composed_of'] = composed_of_list
  #   ## 'highlight' attribute              # non-standard 'property' attribute
  #   dic[u'highlight'] = self.highlight
  #   ## non-attribute info
  #   dic[u'url_software_page'] = u'%s://%s%s#%s' % ( url_scheme, url_server, reverse(u'apps_url',), self.slug )
  #   ## return
  #   return dic

  # end class Software()


### non db models ###


class LoginManager( object ):

  def __init__( self, REQUEST_META_DICT, ADMIN_CONTACT, SPOOFED_SHIB_JSON, PERMITTED_ADMINS, GROUP_NAME ):
    u'''upper-case attributes passed in'''
    self.REQUEST_META_DICT = REQUEST_META_DICT
    self.ADMIN_CONTACT = ADMIN_CONTACT
    self.SPOOFED_SHIB_JSON = SPOOFED_SHIB_JSON
    self.PERMITTED_ADMINS = PERMITTED_ADMINS
    self.GROUP_NAME = GROUP_NAME  # if user needs to be created
    self.forbidden_response = u'You are not authorized to use the admin. If you believe you should be, please contact "%s".' % self.ADMIN_CONTACT
    self.login_name = None  # eppn
    self.first_name, self.last_name, self.email = ( None, None, None )
    self.user = None  # django user-object
    self.authN_check, self.authZ_check, self.login_check = ( u'failure', u'failure', u'failure' )
    try:
      self.login_name = self.REQUEST_META_DICT[ u'Shibboleth-eppn' ]
      self.first_name, self.last_name, self.email = ( self.REQUEST_META_DICT[u'Shibboleth-givenName'], self.REQUEST_META_DICT[u'Shibboleth-sn'], self.REQUEST_META_DICT[u'Shibboleth-mail'].lower() )
      log.debug( u'shib info used' )
    except Exception as e:
      log.debug( u'error trying real shib info: %s' % repr(e).decode(u'utf-8', u'replace') )
      try:
        d = json.loads( self.SPOOFED_SHIB_JSON )
        log.debug( u'd is: %s' % d )
        self.login_name = d[ u'Shibboleth-eppn' ]
        self.first_name, self.last_name, self.email = ( d[u'Shibboleth-givenName'], d[u'Shibboleth-sn'], d[u'Shibboleth-mail'].lower() )
        log.debug( u'spoofed shib info used' )
      except Exception as e2:
        self.login_name = None
        log.debug( u'error using SPOOFED_SHIB_JSON (formatted badly?): %s' % repr(e2).decode(u'utf-8', u'replace') )
    log.debug( u'LoginManager init() end' )

  def check_authN( self ):
    if self.login_name != None:
      self.authN_check = u'success'
    log.debug( u'self.authN_check: %s' % self.authN_check )
    return self.authN_check

  def check_authZ( self ):
    assert self.authN_check == u'success'
    if self.login_name in self.PERMITTED_ADMINS:
      self.authZ_check = u'success'
    log.debug( u'self.authZ_check: %s' % self.authZ_check )
    return self.authZ_check

  def login_user( self, request ):  # request passed in because its session-object is updated
    from django.contrib import auth
    assert self.authN_check == u'success'; assert self.authZ_check == u'success'
    ## get or make user
    try:
      self.user = auth.models.User.objects.get( username=self.login_name )
    except Exception as e:
      log.debug( u'user-object not found: %s -- will create it' % repr(e).decode(u'utf-8', u'replace') )
      self.create_user()
    ## assign group permissions if necessary
    self.check_permissions()
    ## login
    self.user.backend = u'django.contrib.auth.backends.ModelBackend'
    auth.login( request, self.user )
    self.login_check = u'success'
    log.debug( u'self.login_check: %s' % self.login_check )
    return self.login_check

  def create_user( self ):
    from django.contrib.auth.models import User
    user = User( username=self.login_name )
    user.set_unusable_password()
    user.first_name, user.last_name, user.email = ( self.first_name, self.last_name, self.email )
    user.is_staff = True   # allows admin access
    user.save()
    self.user = user
    log.debug( u'user created' )

  def check_permissions( self ):
    from django.contrib.auth.models import Group
    group = Group.objects.get( name=self.GROUP_NAME )
    if not group in self.user.groups.all():
      self.user.groups.add( group )
    log.debug( u'self.user.groups.all(): %s' % self.user.groups.all() )

  # end class LoginManager()
