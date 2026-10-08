import random
from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from expenses.models import Budget, Expense

# (category, description, min amount, max amount, payment method)
TEMPLATES = [
    ("Food", "Groceries", 300, 1800, "UPI"),
    ("Food", "Restaurant", 200, 1200, "Credit Card"),
    ("Transport", "Fuel", 300, 1500, "Cash"),
    ("Transport", "Metro / bus pass", 100, 800, "UPI"),
    ("Shopping", "Clothing", 500, 3500, "Credit Card"),
    ("Bills", "Electricity bill", 800, 2500, "Bank Transfer"),
    ("Bills", "Internet bill", 600, 900, "UPI"),
    ("Entertainment", "Movie / streaming", 150, 900, "Debit Card"),
    ("Health", "Pharmacy", 100, 1500, "Cash"),
    ("Education", "Online course", 500, 2500, "UPI"),
    ("Travel", "Weekend trip", 1000, 6000, "Debit Card"),
    ("Other", "Miscellaneous", 100, 800, "Cash"),
]


class Command(BaseCommand):
    help = "Create a demo user with realistic sample expenses for the last 6 months."

    def add_arguments(self, parser):
        parser.add_argument("--username", default="demo_user")
        parser.add_argument("--password", default="Demo@12345")
        parser.add_argument("--months", type=int, default=6)

    def handle(self, *args, **options):
        random.seed(42)
        user, created = User.objects.get_or_create(username=options["username"], defaults={"email": "demo@example.com"})
        if created:
            user.set_password(options["password"])
            user.save()

        Expense.objects.filter(user=user).delete()
        today = date.today()
        count = 0
        for offset in range(options["months"] - 1, -1, -1):
            total_months = today.year * 12 + (today.month - 1) - offset
            year, month = divmod(total_months, 12)
            month += 1
            growth = 1 + (options["months"] - 1 - offset) * 0.05  # gentle upward trend
            last_day = today.day if offset == 0 else 28
            for _ in range(random.randint(14, 20)):
                category, desc, low, high, method = random.choice(TEMPLATES)
                amount = Decimal(str(round(random.uniform(low, high) * growth, 2)))
                Expense.objects.create(
                    user=user,
                    amount=amount,
                    category=category,
                    date=date(year, month, random.randint(1, max(last_day, 1))),
                    payment_method=method,
                    description=desc,
                )
                count += 1
            if offset == 0:
                Budget.objects.update_or_create(user=user, month=month, year=year, defaults={"amount": Decimal("25000")})

        self.stdout.write(self.style.SUCCESS(f"Created {count} sample expenses for user '{user.username}'."))
        if created:
            self.stdout.write(f"Login with username '{user.username}' and password '{options['password']}'.")
