from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from banking.models import BankAccount, CustomerProfile


class Command(BaseCommand):
    help = "Create the Finova demo administrator and demo customer."

    def handle(self, *args, **options):
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@finovabank.local",
                "first_name": "Bank",
                "last_name": "Administrator",
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
        )

        admin.email = "admin@finovabank.local"
        admin.is_staff = True
        admin.is_superuser = True
        admin.is_active = True
        admin.set_password("Admin@12345")
        admin.save()

        demo, _ = User.objects.get_or_create(
            username="customer",
            defaults={
                "email": "customer@finovabank.local",
                "first_name": "Demo",
                "last_name": "Customer",
                "is_active": True,
            },
        )
        demo.set_password("Customer@12345")
        demo.save()

        CustomerProfile.objects.get_or_create(
            user=demo,
            defaults={
                "phone": "9999999999",
                "address": "Demo Address, Pune",
            },
        )

        account, account_created = BankAccount.objects.get_or_create(
            user=demo,
            defaults={
                "account_type": "SAVINGS",
                "balance": Decimal("25000.00"),
                "minimum_balance": Decimal("1000.00"),
                "status": "ACTIVE",
            },
        )

        self.stdout.write(self.style.SUCCESS(
            "Demo setup completed."
        ))
        self.stdout.write("Admin username: admin")
        self.stdout.write("Admin password: Admin@12345")
        self.stdout.write("Customer username: customer")
        self.stdout.write("Customer password: Customer@12345")
        self.stdout.write(
            f"Customer account: {account.account_number}"
        )
