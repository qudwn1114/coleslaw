# Generated by Django 4.2.13 on 2024-08-02 10:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("system_manage", "0099_orderpayment_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="orderpayment",
            name="payment_method",
            field=models.CharField(default="", max_length=10, verbose_name="결제수단"),
        ),
    ]