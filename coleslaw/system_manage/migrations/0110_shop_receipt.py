# Generated by Django 4.2.13 on 2024-08-06 10:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("system_manage", "0109_alter_orderpayment_created_at_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="shop",
            name="receipt",
            field=models.TextField(default="", verbose_name="영수증내용"),
        ),
    ]
