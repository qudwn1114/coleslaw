# Generated by Django 4.2.13 on 2024-07-25 14:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("system_manage", "0073_remove_ordergoods_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="order_name_en",
            field=models.CharField(max_length=255, null=True, verbose_name="주문영문명"),
        ),
        migrations.AddField(
            model_name="order",
            name="order_name_kr",
            field=models.CharField(max_length=255, null=True, verbose_name="주문한글명"),
        ),
    ]
