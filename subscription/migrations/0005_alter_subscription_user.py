# Generated by Django 4.2.2 on 2023-07-03 18:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("subscription", "0004_alter_subscription_end_date_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="subscription",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="subscriptions",
                to=settings.AUTH_USER_MODEL,
                verbose_name="subscriber",
            ),
        ),
    ]
