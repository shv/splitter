# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-27 21:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('landing', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='abrule',
            name='cnt',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
