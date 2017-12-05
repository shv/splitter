# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Host, Page, CreativeGroup, Creative, CreativePart, Segment, LineItem, ABRule, Order, Product

admin.site.register(Host)
admin.site.register(Page)
admin.site.register(CreativeGroup)
admin.site.register(Creative)
admin.site.register(CreativePart)
admin.site.register(Segment)
admin.site.register(LineItem)
admin.site.register(ABRule)
admin.site.register(Order)
admin.site.register(Product)
