# Generated by Django 4.2.13 on 2024-07-25 15:04

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("system_manage", "0081_remove_ordergoods_option"),
    ]

    operations = [
        migrations.AddField(
            model_name="shopcategory",
            name="name_en",
            field=models.CharField(
                max_length=100, null=True, verbose_name="가맹점카테고리영문이름"
            ),
        ),
        migrations.AddField(
            model_name="shopcategory",
            name="name_kr",
            field=models.CharField(
                max_length=100, null=True, verbose_name="가맹점카테고리한글이름"
            ),
        ),
    ]
