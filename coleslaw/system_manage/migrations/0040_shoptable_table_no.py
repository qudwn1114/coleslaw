# Generated by Django 4.2.13 on 2024-07-07 18:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("system_manage", "0039_alter_shoptable_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="shoptable",
            name="table_no",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
