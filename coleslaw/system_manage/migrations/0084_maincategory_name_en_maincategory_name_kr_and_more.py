# Generated by Django 4.2.13 on 2024-07-25 15:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "system_manage",
            "0083_remove_shopcategory_name_alter_shopcategory_name_en_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="maincategory",
            name="name_en",
            field=models.CharField(max_length=100, null=True, verbose_name="대분류 영문이름"),
        ),
        migrations.AddField(
            model_name="maincategory",
            name="name_kr",
            field=models.CharField(max_length=100, null=True, verbose_name="대분류 한글이름"),
        ),
        migrations.AddField(
            model_name="subcategory",
            name="name_en",
            field=models.CharField(max_length=100, null=True, verbose_name="소분류 영문이름"),
        ),
        migrations.AddField(
            model_name="subcategory",
            name="name_kr",
            field=models.CharField(max_length=100, null=True, verbose_name="소분류 한글이름"),
        ),
    ]
