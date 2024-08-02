# Generated by Django 4.2.13 on 2024-08-02 17:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("system_manage", "0104_checkoutdetail_sale_option_price_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="ordergoods",
            name="sale_option_price",
            field=models.PositiveIntegerField(default=0, verbose_name="당시옵션판매가격"),
        ),
        migrations.AddField(
            model_name="ordergoods",
            name="sale_price",
            field=models.PositiveIntegerField(default=0, verbose_name="당시상품판매가격"),
        ),
    ]
