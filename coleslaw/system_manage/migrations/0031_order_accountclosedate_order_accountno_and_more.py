# Generated by Django 4.2.13 on 2024-06-21 10:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("system_manage", "0030_rename_checkout_detail_ordergoodsoption_order_goods"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="accountCloseDate",
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name="order",
            name="accountNo",
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name="order",
            name="acqCompanyName",
            field=models.CharField(default="", max_length=20),
        ),
        migrations.AddField(
            model_name="order",
            name="acqCompanyNo",
            field=models.CharField(default="", max_length=20),
        ),
        migrations.AddField(
            model_name="order",
            name="amount",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="order",
            name="applNo",
            field=models.CharField(default="", max_length=20),
        ),
        migrations.AddField(
            model_name="order",
            name="bankCode",
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name="order",
            name="billkey",
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name="order",
            name="cardAmount",
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name="order",
            name="cardNo",
            field=models.CharField(default="", max_length=100),
        ),
        migrations.AddField(
            model_name="order",
            name="cardPointAmount",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="order",
            name="cardPointApplNo",
            field=models.CharField(default="", max_length=20),
        ),
        migrations.AddField(
            model_name="order",
            name="couponAmount",
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name="order",
            name="customerTelNo",
            field=models.CharField(default="", max_length=20),
        ),
        migrations.AddField(
            model_name="order",
            name="custormerName",
            field=models.CharField(default="", max_length=50),
        ),
        migrations.AddField(
            model_name="order",
            name="custormmerName",
            field=models.CharField(default="", max_length=50),
        ),
        migrations.AddField(
            model_name="order",
            name="custormmerTelNo",
            field=models.CharField(default="", max_length=50),
        ),
        migrations.AddField(
            model_name="order",
            name="feeAmount",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="order",
            name="goodsName",
            field=models.CharField(default="", max_length=100),
        ),
        migrations.AddField(
            model_name="order",
            name="greenDepositAmount",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="order",
            name="installment",
            field=models.CharField(default="", max_length=20),
        ),
        migrations.AddField(
            model_name="order",
            name="issueCardName",
            field=models.CharField(default="", max_length=20),
        ),
        migrations.AddField(
            model_name="order",
            name="issueCompanyName",
            field=models.CharField(default="", max_length=20),
        ),
        migrations.AddField(
            model_name="order",
            name="issueCompanyNo",
            field=models.CharField(default="", max_length=10),
        ),
        migrations.AddField(
            model_name="order",
            name="mbrNo",
            field=models.CharField(default="", max_length=20),
        ),
        migrations.AddField(
            model_name="order",
            name="mbrRefNo",
            field=models.CharField(default="", max_length=100),
        ),
        migrations.AddField(
            model_name="order",
            name="payType",
            field=models.CharField(default="", max_length=10),
        ),
        migrations.AddField(
            model_name="order",
            name="pointAmount",
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name="order",
            name="taxAmount",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="order",
            name="taxFreeAmount",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="order",
            name="tranDate",
            field=models.CharField(default="", max_length=20),
        ),
        migrations.AddField(
            model_name="order",
            name="tranTime",
            field=models.CharField(default="", max_length=20),
        ),
    ]