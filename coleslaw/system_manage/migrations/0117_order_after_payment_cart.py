# Generated by Django 4.2.13 on 2024-08-08 09:44

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("system_manage", "0116_goods_after_payment_goods"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="after_payment_cart",
            field=models.TextField(null=True, verbose_name="결제이후 장바구니 상품"),
        ),
    ]
