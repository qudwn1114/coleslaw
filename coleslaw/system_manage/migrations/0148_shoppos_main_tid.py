# Generated by Django 4.2.14 on 2025-03-21 17:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("system_manage", "0147_shoppos_shoppos_shop_pos_unique"),
    ]

    operations = [
        migrations.AddField(
            model_name="shoppos",
            name="main_tid",
            field=models.CharField(default="", max_length=20, verbose_name="메인 tid"),
        ),
    ]
