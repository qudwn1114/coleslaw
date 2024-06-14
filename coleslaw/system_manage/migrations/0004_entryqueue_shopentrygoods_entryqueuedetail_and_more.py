# Generated by Django 4.2.13 on 2024-06-14 12:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("system_manage", "0003_remove_goods_sold_out_goods_status_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="EntryQueue",
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
                ("order", models.PositiveIntegerField()),
                ("date", models.DateField(auto_now_add=True, verbose_name="날짜")),
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
                "db_table": "entry_queue",
            },
        ),
        migrations.CreateModel(
            name="ShopEntryGoods",
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
                ("sequence", models.IntegerField(verbose_name="순서")),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="생성일"),
                ),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="수정일")),
                (
                    "goods",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="system_manage.goods",
                    ),
                ),
                (
                    "shop",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="system_manage.shop",
                    ),
                ),
            ],
            options={
                "db_table": "shop_entry_goods",
            },
        ),
        migrations.CreateModel(
            name="EntryQueueDetail",
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
                ("quantity", models.PositiveIntegerField(default=1, verbose_name="수량")),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="생성일"),
                ),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="수정일")),
                (
                    "entry_queue",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="system_manage.entryqueue",
                    ),
                ),
                (
                    "goods",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="system_manage.goods",
                    ),
                ),
            ],
            options={
                "db_table": "entry_queue_detail",
            },
        ),
        migrations.AddConstraint(
            model_name="shopentrygoods",
            constraint=models.UniqueConstraint(
                fields=("shop", "sequence"), name="shop_sequence_unique"
            ),
        ),
        migrations.AddConstraint(
            model_name="entryqueue",
            constraint=models.UniqueConstraint(
                fields=("shop", "order", "date"), name="shop_order_date_unique"
            ),
        ),
    ]
