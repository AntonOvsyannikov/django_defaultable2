# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2019-07-28 23:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import dm.defaultable.models
import dm.defaultable.stuff
import functools


class Migration(migrations.Migration):

    dependencies = [
        ('dm', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModelX',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('isDefault', models.BooleanField(default=False)),
                ('f', models.FileField(default='*myfile.txt', max_length=1024, upload_to=dm.defaultable.models.upload_to)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='mymodel',
            name='x',
            field=models.ForeignKey(default=functools.partial(dm.defaultable.stuff.get_or_create_default, *(b'ModelX', b'dm'), **{}), on_delete=django.db.models.deletion.SET_DEFAULT, to='dm.ModelX'),
        ),
    ]