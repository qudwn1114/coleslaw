# Generated by Django 4.2.13 on 2024-08-01 13:04

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        (
            "system_manage",
            "0096_checkout_final_additional_order_final_additional_and_more",
        ),
    ]

    operations = [
        migrations.RemoveField(
            model_name="order",
            name="cancelled_at",
        ),
    ]
