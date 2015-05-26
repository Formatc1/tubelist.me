# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Playlist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.CharField(unique=True, max_length=32)),
                ('name', models.CharField(max_length=100)),
                ('author', models.EmailField(max_length=254, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('identifier', models.SlugField(max_length=20)),
                ('name', models.CharField(max_length=200)),
                ('order', models.PositiveSmallIntegerField()),
                ('playlist', models.ForeignKey(to='playlists.Playlist')),
            ],
        ),
    ]
