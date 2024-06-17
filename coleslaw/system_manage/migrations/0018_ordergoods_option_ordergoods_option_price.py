# Generated by Django 4.2.13 on 2024-06-18 01:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("system_manage", "0017_checkout_agency"),
    ]

    operations = [
        migrations.AddField(
            model_name="ordergoods",
            name="option",
            field=models.CharField(max_length=200, null=True, verbose_name="옵션"),
        ),
        migrations.AddField(
            model_name="ordergoods",
            name="option_price",
            field=models.PositiveIntegerField(default=0, verbose_name="옵션추가비용"),
        ),
    ]
