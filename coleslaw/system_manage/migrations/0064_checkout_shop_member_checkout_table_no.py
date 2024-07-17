# Generated by Django 4.2.13 on 2024-07-17 12:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("system_manage", "0063_alter_order_table_no"),
    ]

    operations = [
        migrations.AddField(
            model_name="checkout",
            name="shop_member",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="system_manage.shopmember",
            ),
        ),
        migrations.AddField(
            model_name="checkout",
            name="table_no",
            field=models.PositiveIntegerField(default=None, null=True),
        ),
    ]