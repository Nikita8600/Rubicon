from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):
    dependencies = [
        ("banking", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="card",
            name="max_transactions_per_day",
            field=models.PositiveSmallIntegerField(default=4),
        ),
        migrations.AlterField(
            model_name="card",
            name="daily_limit",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("20000.00"),
                max_digits=12,
            ),
        ),
        migrations.AddField(
            model_name="loan",
            name="salary",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("0.01"),
                max_digits=15,
                validators=[django.core.validators.MinValueValidator(Decimal("0.01"))],
            ),
        ),
        migrations.AddField(
            model_name="transaction",
            name="card",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="transactions",
                to="banking.card",
            ),
        ),
    ]
