# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Host(models.Model):
    title = models.CharField(max_length=255)
    domain = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return "%s" % (self.domain)

    class Meta:
        ordering = ('title',)


@python_2_unicode_compatible
class Page(models.Model):
    title = models.CharField(max_length=255)
    url = models.CharField(max_length=255, blank=True)
    template = models.CharField(max_length=255)
    purpose = models.CharField(max_length=16, blank=True)
    host = models.ForeignKey(
        'Host',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return "%s" % (self.title)

    class Meta:
        ordering = ('title',)
        unique_together = ('url', 'host',)


@python_2_unicode_compatible
class Creative(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    creativegroup = models.ForeignKey(
        'CreativeGroup',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return "%s" % (self.title)

    class Meta:
        ordering = ('title',)


@python_2_unicode_compatible
class CreativePart(models.Model):
    name = models.CharField(max_length=255)
    content = models.TextField()
    executable = models.BooleanField()
    creatives = models.ManyToManyField(Creative, blank=True)
    creativegroup = models.ForeignKey(
        'CreativeGroup',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return "{} => {}".format(self.name, self.content)

    class Meta:
        ordering = ('name',)


@python_2_unicode_compatible
class CreativeGroup(models.Model):
    title = models.CharField(max_length=255)
    pages = models.ManyToManyField(Page, blank=False)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('title',)


@python_2_unicode_compatible
class Segment(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()

    def __str__(self):
        return "%s" % (self.title)

    class Meta:
        ordering = ('title',)


@python_2_unicode_compatible
class LineItem(models.Model):
    title = models.CharField(max_length=255)
    segment = models.ForeignKey(
        'Segment',
        on_delete=models.CASCADE,
    )
    priority = models.IntegerField()
    page = models.ForeignKey(Page, on_delete=models.CASCADE)

    def __str__(self):
        return "%s" % (self.title)

    class Meta:
        ordering = ('title',)


@python_2_unicode_compatible
class ABRule(models.Model):
    percentage = models.IntegerField()
    creative = models.ForeignKey(
        'Creative',
        on_delete=models.CASCADE,
    )
    line_item = models.ForeignKey(
        'LineItem',
        on_delete=models.CASCADE,
    )
    cnt = models.IntegerField()

    def __str__(self):
        return "%s: %s" % (self.percentage, self.creative)

    class Meta:
        ordering = ('percentage',)


@python_2_unicode_compatible
class Order(models.Model):
    phone = models.CharField(max_length=255)
    description = models.TextField()
    session_id = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return "%s [%s]: %s. %s (%s)" % (self.pk, self.status, self.phone, self.description, self.created)

    class Meta:
        ordering = ('-created',)
