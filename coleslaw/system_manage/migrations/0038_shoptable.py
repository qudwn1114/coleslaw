# Generated by Django 4.2.13 on 2024-07-04 18:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("system_manage", "0037_shoppersontype_delete_shopentrypersontype_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="ShopTable",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, verbose_name="대분류이름")),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="생성일"),
                ),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="수정일")),
                (
                    "shop",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="system_manage.shop",
                    ),
                ),
            ],
            options={
                "db_table": "shop_table",
            },
        ),
    ]
