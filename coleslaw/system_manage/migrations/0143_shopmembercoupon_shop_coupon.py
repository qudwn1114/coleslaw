# Generated by Django 4.2.14 on 2025-02-25 18:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("system_manage", "0142_remove_shopcoupon_coupon_type_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="shopmembercoupon",
            name="shop_coupon",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="shop_member_coupon",
                to="system_manage.shopcoupon",
            ),
        ),
    ]
