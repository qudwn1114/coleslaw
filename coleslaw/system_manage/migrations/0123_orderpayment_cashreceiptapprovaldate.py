# Generated by Django 4.2.14 on 2024-08-21 20:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("system_manage", "0122_orderpayment_cashresceiptstatus"),
    ]

    operations = [
        migrations.AddField(
            model_name="orderpayment",
            name="cashReceiptApprovalDate",
            field=models.CharField(default="", max_length=20),
        ),
    ]
