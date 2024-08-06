# Generated by Django 4.2.13 on 2024-08-06 14:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("system_manage", "0113_shop_shop_receipt_flag"),
    ]

    operations = [
        migrations.AddField(
            model_name="shop",
            name="additional_fee_time",
            field=models.PositiveIntegerField(default=10, verbose_name="테이블이용시간"),
        ),
        migrations.AddField(
            model_name="shop",
            name="table_time",
            field=models.PositiveIntegerField(default=0, verbose_name="테이블이용시간"),
        ),
    ]