from django.contrib import admin

from .models import Budget, Expense


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "amount", "category", "payment_method", "date")
    list_filter = ("category", "payment_method", "date")
    search_fields = ("description", "user__username")
    date_hierarchy = "date"


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "month", "year", "amount", "created_at")
    list_filter = ("year", "month")
    search_fields = ("user__username",)
