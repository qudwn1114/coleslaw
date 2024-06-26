# Generated by Django 4.2.13 on 2024-06-21 11:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("system_manage", "0031_order_accountclosedate_order_accountno_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ordergoodsoption",
            name="order_goods",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="order_goods_option",
                to="system_manage.ordergoods",
            ),
        ),
    ]
