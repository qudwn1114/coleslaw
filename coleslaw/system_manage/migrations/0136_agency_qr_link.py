# Generated by Django 4.2.14 on 2024-10-08 20:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("system_manage", "0135_shop_tbridge"),
    ]

    operations = [
        migrations.AddField(
            model_name="agency",
            name="qr_link",
            field=models.CharField(max_length=300, null=True, verbose_name="qr주문 링크"),
        ),
    ]
