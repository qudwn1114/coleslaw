# Generated by Django 4.2.13 on 2024-07-07 19:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("system_manage", "0041_alter_shoptable_table_no_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="shoppersontype",
            name="goods",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="system_manage.goods",
            ),
        ),
    ]
