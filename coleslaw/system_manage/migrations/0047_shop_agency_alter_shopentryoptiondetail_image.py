# Generated by Django 4.2.13 on 2024-07-09 16:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("system_manage", "0046_remove_shopentryoptiondetail_image_thumbnail"),
    ]

    operations = [
        migrations.AddField(
            model_name="shop",
            name="agency",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="shop",
                to="system_manage.agency",
                verbose_name="메인 agency",
            ),
        ),
        migrations.AlterField(
            model_name="shopentryoptiondetail",
            name="image",
            field=models.ImageField(
                default="image/goods/default.jpg",
                max_length=300,
                upload_to="image/shop_entry_option/%Y/%m/%d/",
                verbose_name="옵션이미지",
            ),
        ),
    ]
