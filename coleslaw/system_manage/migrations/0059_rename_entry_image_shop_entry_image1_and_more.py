# Generated by Django 4.2.13 on 2024-07-11 19:15

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("system_manage", "0058_shoptable_total_price"),
    ]

    operations = [
        migrations.RenameField(
            model_name="shop",
            old_name="entry_image",
            new_name="entry_image1",
        ),
        migrations.RenameField(
            model_name="shop",
            old_name="logo_image",
            new_name="logo_image1",
        ),
    ]
