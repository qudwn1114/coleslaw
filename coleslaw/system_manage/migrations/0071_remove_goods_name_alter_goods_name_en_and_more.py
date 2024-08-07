# Generated by Django 4.2.13 on 2024-07-25 12:10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("system_manage", "0070_goods_name_en_goods_name_kr"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="goods",
            name="name",
        ),
        migrations.AlterField(
            model_name="goods",
            name="name_en",
            field=models.CharField(max_length=100, verbose_name="상품영문명"),
        ),
        migrations.AlterField(
            model_name="goods",
            name="name_kr",
            field=models.CharField(max_length=100, verbose_name="상품한글명"),
        ),
    ]
