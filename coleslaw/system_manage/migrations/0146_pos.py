# Generated by Django 4.2.14 on 2025-03-21 16:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("system_manage", "0145_remove_entryqueue_shop_member"),
    ]

    operations = [
        migrations.CreateModel(
            name="Pos",
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
                ("name", models.CharField(max_length=50, verbose_name="포스업체명")),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="생성일"),
                ),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="수정일")),
            ],
            options={
                "db_table": "pos",
            },
        ),
    ]
