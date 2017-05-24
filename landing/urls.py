# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^create-order$', views.create_order, name='create_order'),
    url(r'^generate$', views.generate, name='generate'),
    url(r'^(?P<url>.*)$', views.landing, name='landing'),
]

