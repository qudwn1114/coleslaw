# Generated by Django 4.2.13 on 2024-07-25 12:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("system_manage", "0069_remove_shop_name_alter_shop_name_en_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="goods",
            name="name_en",
            field=models.CharField(max_length=100, null=True, verbose_name="상품영문명"),
        ),
        migrations.AddField(
            model_name="goods",
            name="name_kr",
            field=models.CharField(max_length=100, null=True, verbose_name="상품한글명"),
        ),
    ]