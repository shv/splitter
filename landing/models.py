# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class Host(models.Model):
    title = models.CharField(max_length=255)
    domain = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return "%s" % (self.domain)

    class Meta:
        ordering = ('title',)


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


class CreativeGroup(models.Model):
    title = models.CharField(max_length=255)
    pages = models.ManyToManyField(Page, blank=False)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('title',)


class Segment(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()

    def __str__(self):
        return "%s" % (self.title)

    class Meta:
        ordering = ('title',)


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
