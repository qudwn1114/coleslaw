# Generated by Django 4.2.13 on 2024-07-25 14:26

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("system_manage", "0078_remove_goodsoption_name"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="goodsoptiondetail",
            name="name",
        ),
    ]
