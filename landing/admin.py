# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Page, Creative, CreativePart, Segment, LineItem, ABRule

admin.site.register(Page)
admin.site.register(Creative)
admin.site.register(CreativePart)
admin.site.register(Segment)
admin.site.register(LineItem)
admin.site.register(ABRule)
