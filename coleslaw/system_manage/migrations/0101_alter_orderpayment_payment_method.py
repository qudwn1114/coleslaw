# Generated by Django 4.2.13 on 2024-08-02 10:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("system_manage", "0100_orderpayment_payment_method"),
    ]

    operations = [
        migrations.AlterField(
            model_name="orderpayment",
            name="payment_method",
            field=models.CharField(default="0", max_length=10, verbose_name="결제수단"),
        ),
    ]