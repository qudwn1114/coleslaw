# Generated by Django 4.2.13 on 2024-07-17 18:05

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        (
            "system_manage",
            "0066_checkout_final_discount_checkoutdetail_discount_and_more",
        ),
    ]

    operations = [
        migrations.RemoveField(
            model_name="checkoutdetail",
            name="discount",
        ),
    ]
