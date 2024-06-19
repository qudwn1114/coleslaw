# Generated by Django 4.2.13 on 2024-06-18 15:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("system_manage", "0020_alter_ordergoods_option"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="agency",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="system_manage.agency",
            ),
        ),
    ]