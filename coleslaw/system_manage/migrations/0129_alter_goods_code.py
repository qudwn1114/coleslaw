# Generated by Django 4.2.14 on 2024-08-27 18:44

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("system_manage", "0128_goods_code"),
    ]

    operations = [
        migrations.AlterField(
            model_name="goods",
            name="code",
            field=models.CharField(max_length=20, unique=True, verbose_name="상품코드"),
        ),
    ]
