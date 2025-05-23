# Generated by Django 4.2.14 on 2025-04-29 19:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "system_manage",
            "0158_remove_subcategory_main_category_name_kr_unique_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="maincategory",
            name="name_en",
            field=models.CharField(max_length=100, verbose_name="대분류 영문이름"),
        ),
        migrations.AlterField(
            model_name="maincategory",
            name="name_kr",
            field=models.CharField(max_length=100, verbose_name="대분류 한글이름"),
        ),
        migrations.AddConstraint(
            model_name="maincategory",
            constraint=models.UniqueConstraint(
                fields=("shop", "name_kr"), name="shop_name_kr_unique"
            ),
        ),
        migrations.AddConstraint(
            model_name="maincategory",
            constraint=models.UniqueConstraint(
                fields=("shop", "name_en"), name="shop_name_en_unique"
            ),
        ),
    ]
