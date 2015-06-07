# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('playlists', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 7, 16, 28, 27, 635000, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
