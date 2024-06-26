# Generated by Django 4.2.13 on 2024-06-14 14:36

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("system_manage", "0004_entryqueue_shopentrygoods_entryqueuedetail_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="entryqueue",
            name="car_plate_no",
            field=models.CharField(default="", max_length=20, verbose_name="차량번호"),
        ),
        migrations.AddField(
            model_name="entryqueue",
            name="membername",
            field=models.CharField(max_length=20, null=True, verbose_name="예약자명"),
        ),
        migrations.AddField(
            model_name="entryqueue",
            name="phone",
            field=models.CharField(max_length=20, null=True, verbose_name="전화번호"),
        ),
    ]
