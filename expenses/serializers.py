from datetime import date

from rest_framework import serializers

from .models import Budget, Expense


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ["id", "amount", "category", "date", "payment_method", "description", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def validate_date(self, value):
        if value > date.today():
            raise serializers.ValidationError("Expense date cannot be in the future.")
        return value


class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = ["id", "month", "year", "amount", "created_at"]
        read_only_fields = ["id", "created_at"]
