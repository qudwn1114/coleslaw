# Generated by Django 4.2.13 on 2024-07-25 11:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("system_manage", "0068_shop_name_en_shop_name_kr_alter_shop_name"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="shop",
            name="name",
        ),
        migrations.AlterField(
            model_name="shop",
            name="name_en",
            field=models.CharField(max_length=100, unique=True, verbose_name="가맹점영문명"),
        ),
        migrations.AlterField(
            model_name="shop",
            name="name_kr",
            field=models.CharField(max_length=100, unique=True, verbose_name="가맹점한글명"),
        ),
    ]
