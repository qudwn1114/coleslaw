# Generated by Django 4.2.14 on 2024-08-21 20:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "system_manage",
            "0124_rename_cashreceiptcardno_orderpayment_cashreceiptcardno",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="shoptable",
            name="exit_color",
            field=models.CharField(
                default="2c70f5", max_length=20, verbose_name="퇴장하기 버튼 색"
            ),
        ),
    ]
