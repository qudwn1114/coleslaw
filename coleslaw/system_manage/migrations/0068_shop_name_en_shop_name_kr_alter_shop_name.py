# Generated by Django 4.2.13 on 2024-07-25 11:22

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("system_manage", "0067_remove_checkoutdetail_discount"),
    ]

    operations = [
        migrations.AddField(
            model_name="shop",
            name="name_en",
            field=models.CharField(max_length=100, null=True, verbose_name="가맹점영문명"),
        ),
        migrations.AddField(
            model_name="shop",
            name="name_kr",
            field=models.CharField(max_length=100, null=True, verbose_name="가맹점한글명"),
        ),
        migrations.AlterField(
            model_name="shop",
            name="name",
            field=models.CharField(max_length=100, unique=True, verbose_name="가맹점한글명"),
        ),
    ]
