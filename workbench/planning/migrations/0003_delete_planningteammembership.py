# Generated by Django 3.1b1 on 2020-07-11 08:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("planning", "0002_plannedwork_title"),
    ]

    operations = [
        migrations.DeleteModel(
            name="PlanningTeamMembership",
        ),
    ]
