# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-11-10 22:14
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tipos', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='documento',
            name='tipo_documento',
        ),
        migrations.DeleteModel(
            name='Documento',
        ),
    ]