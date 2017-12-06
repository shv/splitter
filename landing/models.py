# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils.encoding import python_2_unicode_compatible

# Фикс кодировки JSON полей в админке для питона 3
import json
from django.contrib.postgres.forms.jsonb import (
    InvalidJSONInput,
    JSONField as JSONFormField,
)


class UTF8JSONFormField(JSONFormField):

    def prepare_value(self, value):
        if isinstance(value, InvalidJSONInput):
            return value
        return json.dumps(value, ensure_ascii=False)


class UTF8JSONField(JSONField):
    """JSONField for postgres databases.

    Displays UTF-8 characters directly in the admin, i.e. äöü instead of
    unicode escape sequences.
    """

    def formfield(self, **kwargs):
        return super().formfield(**{
            **{'form_class': UTF8JSONFormField},
            **kwargs,
        })


@python_2_unicode_compatible
class Host(models.Model):
    title = models.CharField(max_length=255)
    domain = models.CharField(max_length=255, unique=True)
    telegramm_token = models.CharField(max_length=255, blank=True)
    telegramm_chat_id = models.CharField(max_length=255, blank=True)
    yandex_metrica_id = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return "%s" % (self.domain)

    class Meta:
        ordering = ('title',)


@python_2_unicode_compatible
class Page(models.Model):
    title = models.CharField(max_length=255)
    # Название страницы
    main_menu = models.CharField(max_length=255, blank=True, null=True)
    # Телефон
    phone_number = models.CharField(max_length=255, blank=True, null=True)
    # Логотип
    logo_url = models.CharField(max_length=255, blank=True, null=True)
    # Полное описание
    left_html = models.TextField(blank=True, null=True)
    # Видео
    right_html = models.TextField(blank=True, null=True)
    # Характеристики
    parameters = UTF8JSONField(blank=True, null=True)
    # Текст в секции action1
    action1_html = models.TextField(blank=True, null=True)
    # Текст в секции action2
    action2_html = models.TextField(blank=True, null=True)
    # Вспомогательные страницы в меню
    add_menu = UTF8JSONField(blank=True, null=True)

    url = models.CharField(max_length=255, blank=True)
    template = models.CharField(max_length=255)
    purpose = models.CharField(max_length=16, blank=True)
    host = models.ForeignKey(
        'Host',
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        'Product',
        on_delete=models.SET_NULL,
        blank=True, null=True
    )
    # Номер по порядку
    ordering = models.IntegerField(blank=True, null=True)

    parent_page = models.ForeignKey(
        'Page',
        on_delete=models.SET_NULL,
        blank=True, null=True
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
    host = models.ForeignKey(
        'Host',
        on_delete=models.SET_NULL,
        blank=True,
        default=None,
        null=True
    )
    page = models.ForeignKey(
        'Page',
        on_delete=models.SET_NULL,
        blank=True,
        default=None,
        null=True
    )

    def __str__(self):
        return "%s [%s]: %s. %s (%s)" % (self.pk, self.status, self.phone, self.description, self.created)

    class Meta:
        ordering = ('-created',)


@python_2_unicode_compatible
class Product(models.Model):
    # Название
    title = models.CharField(max_length=255, blank=True, null=True)
    # Альтернативное название
    alt_title = models.CharField(max_length=255, blank=True, null=True)
    # Конечная цена продажи без доставки
    price = models.IntegerField(blank=True, null=True)
    # Если нет, то из настроек сайта
    delivery_price = models.IntegerField(blank=True, null=True)
    # Главная картинка
    main_image_url = models.CharField(max_length=255, blank=True, null=True)
    # Вторая картинка
    second_image_url = models.CharField(max_length=255, blank=True, null=True)
    # Остальные картинки
    images = UTF8JSONField(blank=True, null=True)
    # Краткое описание
    short_desc = models.TextField(blank=True, null=True)
    # Полное описание
    description = models.TextField(blank=True, null=True)
    # Список фич
    feature_desc = models.TextField(blank=True, null=True)
    # Описание на странице заказа
    order_desc = models.TextField(blank=True, null=True)
    # Характеристики
    parameters = UTF8JSONField(blank=True, null=True)

    def __str__(self): # __unicode__ on Python 2
        return "%s" % (self.title)

    def full_price(self):
        return self.price + self.delivery_price

    def image_urls(self):
        urls = []
        # if self.main_image_url:
        #     urls.append(self.main_image_url)
        # if self.second_image_url:
        #     urls.append(self.second_image_url)
        if isinstance(self.images, list):
            for image in self.images:
                if isinstance(image, dict) and "url" in image:
                    urls.append(image["url"])
        return urls

    # class Meta:
        # ordering = ('ordering',)
        # unique_together = ('url', 'page',)

