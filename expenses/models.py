from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Expense(models.Model):
    class Category(models.TextChoices):
        FOOD = "Food", "Food"
        TRANSPORT = "Transport", "Transport"
        SHOPPING = "Shopping", "Shopping"
        BILLS = "Bills", "Bills"
        ENTERTAINMENT = "Entertainment", "Entertainment"
        HEALTH = "Health", "Health"
        EDUCATION = "Education", "Education"
        TRAVEL = "Travel", "Travel"
        OTHER = "Other", "Other"

    class PaymentMethod(models.TextChoices):
        CASH = "Cash", "Cash"
        UPI = "UPI", "UPI"
        CREDIT_CARD = "Credit Card", "Credit Card"
        DEBIT_CARD = "Debit Card", "Debit Card"
        BANK_TRANSFER = "Bank Transfer", "Bank Transfer"
        OTHER = "Other", "Other"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="expenses")
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER)
    date = models.DateField()
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.UPI)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        indexes = [
            models.Index(fields=["user", "date"]),
            models.Index(fields=["user", "category"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.category} - {self.amount} on {self.date}"


class Budget(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="budgets")
    month = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    year = models.PositiveSmallIntegerField(validators=[MinValueValidator(2000), MaxValueValidator(2100)])
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-year", "-month"]
        constraints = [
            models.UniqueConstraint(fields=["user", "month", "year"], name="unique_budget_per_user_month"),
        ]

    def __str__(self):
        return f"{self.user} - {self.month}/{self.year}: {self.amount}"
