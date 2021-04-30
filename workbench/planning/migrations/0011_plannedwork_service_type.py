# Generated by Django 3.2 on 2021-04-30 08:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("services", "0005_servicetype_color"),
        ("planning", "0010_alter_plannedwork_created_by"),
    ]

    operations = [
        migrations.AddField(
            model_name="plannedwork",
            name="service_type",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="services.servicetype",
                verbose_name="primary service type",
            ),
        ),
    ]
