# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-23 20:38
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0009_auto_20160922_1331'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('invoices', '0004_auto_20160917_2112'),
        ('offers', '0006_auto_20160922_2218'),
        ('logbook', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LoggedCost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created at')),
                ('rendered_on', models.DateField(default=datetime.date.today, verbose_name='rendered on')),
                ('cost', models.DecimalField(decimal_places=2, help_text='The amount we did have to pay.', max_digits=10, verbose_name='cost')),
                ('description', models.TextField(verbose_name='description')),
                ('archived_at', models.DateTimeField(blank=True, null=True, verbose_name='archived at')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='created by')),
                ('invoice', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='invoices.Invoice', verbose_name='invoice')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='loggedcosts', to='projects.Project', verbose_name='project')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='loggedcosts', to='offers.Service', verbose_name='service')),
            ],
            options={
                'verbose_name': 'logged cost',
                'verbose_name_plural': 'logged cost',
                'ordering': ('-rendered_on', '-created_at'),
            },
        ),
    ]
