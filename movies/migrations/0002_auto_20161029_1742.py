# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-29 17:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='similar',
            name='movie',
        ),
        migrations.RemoveField(
            model_name='similar',
            name='sim1',
        ),
        migrations.RemoveField(
            model_name='similar',
            name='sim2',
        ),
        migrations.RemoveField(
            model_name='similar',
            name='sim3',
        ),
        migrations.RemoveField(
            model_name='similar',
            name='sim4',
        ),
        migrations.RemoveField(
            model_name='similar',
            name='sim5',
        ),
        migrations.AddField(
            model_name='movie',
            name='similars',
            field=models.ManyToManyField(to='movies.Movie'),
        ),
        migrations.DeleteModel(
            name='Similar',
        ),
    ]
