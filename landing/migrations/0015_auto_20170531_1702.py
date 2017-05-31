# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-31 17:02
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('landing', '0014_auto_20170524_2218'),
    ]

    operations = [
        migrations.AddField(
            model_name='host',
            name='telegramm_chat_id',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='host',
            name='telegramm_token',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='order',
            name='host',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='landing.Host'),
        ),
        migrations.AddField(
            model_name='order',
            name='page',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='landing.Page'),
        ),
    ]
