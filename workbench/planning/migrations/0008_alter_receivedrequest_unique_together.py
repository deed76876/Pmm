# Generated by Django 3.2a1 on 2021-02-21 11:58

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("planning", "0007_planningrequest_receivers"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="receivedrequest",
            unique_together={("user", "request")},
        ),
    ]
