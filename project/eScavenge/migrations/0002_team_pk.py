# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-30 17:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eScavenge', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='team',
            name='id',
        ),
        migrations.AlterField(
            model_name='team',
            name='password',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='team',
            name='username',
            field=models.TextField(primary_key=True, serialize=False),
        ),
    ]
