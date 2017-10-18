# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('firstapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='receiverhooks',
            name='download_receiver',
            field=models.CharField(help_text=b'\xe5\xaf\xbc\xe5\x85\xa5\xe6\x95\xb0\xe6\x8d\xae\xe7\x9a\x84\xe6\x8e\xa5\xe6\x94\xb6\xe5\x99\xa8\xe5\x9c\xb0\xe5\x9d\x80', max_length=500, null=True, blank=True),
        ),
    ]
