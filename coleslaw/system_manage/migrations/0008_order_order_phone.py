# Generated by Django 4.2.13 on 2024-06-14 19:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("system_manage", "0007_checkout_order_entryqueue_status_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="order_phone",
            field=models.CharField(default="", max_length=20, verbose_name="주문자번호"),
        ),
    ]
