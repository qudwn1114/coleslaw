# Generated by Django 4.2.13 on 2024-07-09 20:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("system_manage", "0049_agencyadmin_agencyadmin_agency_user_unique"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="agency",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="system_manage.agency",
            ),
        ),
    ]