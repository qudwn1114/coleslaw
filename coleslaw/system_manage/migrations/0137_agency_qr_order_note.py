# Generated by Django 4.2.14 on 2024-10-12 01:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("system_manage", "0136_agency_qr_link"),
    ]

    operations = [
        migrations.AddField(
            model_name="agency",
            name="qr_order_note",
            field=models.TextField(default="", null=True),
        ),
    ]
