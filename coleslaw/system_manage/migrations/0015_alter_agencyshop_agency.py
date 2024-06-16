# Generated by Django 4.2.13 on 2024-06-16 16:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("system_manage", "0014_agency_agencyshop_agencyshop_agency_shop_unique"),
    ]

    operations = [
        migrations.AlterField(
            model_name="agencyshop",
            name="agency",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="agency_shop",
                to="system_manage.agency",
            ),
        ),
    ]
