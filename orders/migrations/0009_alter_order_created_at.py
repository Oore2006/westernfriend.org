# Generated by Django 5.0.6 on 2024-05-29 19:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0008_order_paypal_transaction_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
