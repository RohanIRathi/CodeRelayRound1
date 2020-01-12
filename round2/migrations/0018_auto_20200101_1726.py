# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2020-01-01 17:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('round2', '0017_auto_20200101_1725'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='score',
            name='user_f',
        ),
        migrations.AddField(
            model_name='score',
            name='user1_f',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='round2.User1'),
        ),
        migrations.AddField(
            model_name='score',
            name='user2_f',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='round2.User2'),
        ),
    ]