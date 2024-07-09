# Generated by Django 4.2.13 on 2024-07-09 16:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("system_manage", "0048_alter_shop_agency_alter_shop_shop_category"),
    ]

    operations = [
        migrations.CreateModel(
            name="AgencyAdmin",
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
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="생성일"),
                ),
                (
                    "agency",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="system_manage.agency",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="agency_admin",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "agency_admin",
            },
        ),
        migrations.AddConstraint(
            model_name="agencyadmin",
            constraint=models.UniqueConstraint(
                fields=("agency", "user"), name="agency_user_unique"
            ),
        ),
    ]
