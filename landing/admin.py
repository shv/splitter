# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Host, Page, CreativeGroup, Creative, CreativePart, Segment, LineItem, ABRule, Order, Product

admin.site.register(Host)
admin.site.register(CreativeGroup)
admin.site.register(Creative)
admin.site.register(CreativePart)
admin.site.register(Segment)
admin.site.register(LineItem)
admin.site.register(ABRule)


class OrderAdmin(admin.ModelAdmin):
	list_display = ('id', 'status', 'phone', 'fio', 'host', 'page', 'product')

class PageAdmin(admin.ModelAdmin):
	list_display = ('id', 'host', 'url', 'parent_page', 'product', 'title')

class ProductAdmin(admin.ModelAdmin):
	list_display = ('id', 'title', 'price', 'delivery_price', 'full_price')


admin.site.register(Order, OrderAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(Product, ProductAdmin)
