# Generated by Django 4.2.14 on 2025-04-01 19:13

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("system_manage", "0152_remove_shoptable_shop_table_no_unique_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="orderpayment",
            old_name="cashResceiptStatus",
            new_name="cashReceiptStatus",
        ),
    ]
