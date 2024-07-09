# Generated by Django 4.2.13 on 2024-07-10 01:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("system_manage", "0052_rename_logo_shop_logo_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="entryqueue",
            name="remark",
            field=models.TextField(null=True, verbose_name="비고"),
        ),
        migrations.AddField(
            model_name="entryqueue",
            name="shop_member",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="system_manage.shopmember",
            ),
        ),
        migrations.AlterField(
            model_name="shop",
            name="entry_image",
            field=models.ImageField(
                max_length=300,
                null=True,
                upload_to="image/shop_entry/",
                verbose_name="가맹점 입장이미지",
            ),
        ),
        migrations.AlterField(
            model_name="shopmember",
            name="phone",
            field=models.CharField(max_length=30, verbose_name="전화번호"),
        ),
        migrations.AddConstraint(
            model_name="shopmember",
            constraint=models.UniqueConstraint(
                fields=("shop", "phone"), name="shop_phone_unique"
            ),
        ),
    ]
