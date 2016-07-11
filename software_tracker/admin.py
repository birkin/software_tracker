# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.contrib import admin
from software_tracker.models import Software


class SoftwareAdmin(admin.ModelAdmin):
  ordering = [ 'name' ]
  list_display = [ 'name', 'audience', 'activity', 'contact_technical_email' ]
  list_filter = [ 'activity', 'api', 'audience', 'license_name' ]
  search_fields = [ 'name' ]
  prepopulated_fields = { u'slug': (u'name',) }
  # readonly_fields = [ 'code', 'settlement_code', 'region_code' ]


admin.site.register( Software, SoftwareAdmin )
