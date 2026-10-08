from datetime import date

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from . import services
from .forms import BudgetForm, ExpenseFilterForm, ExpenseForm, RegisterForm
from .models import Budget, Expense


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Welcome! Your account has been created.")
        return redirect("dashboard")
    return render(request, "registration/register.html", {"form": form})


@login_required
def dashboard(request):
    summary = services.dashboard_summary(request.user)
    insights = services.build_insights(request.user)
    return render(request, "expenses/dashboard.html", {"summary": summary, "insights": insights})


@login_required
def expense_list(request):
    # Always start from the logged-in user's expenses only.
    qs = Expense.objects.filter(user=request.user)
    form = ExpenseFilterForm(request.GET or None)
    if form.is_valid():
        data = form.cleaned_data
        if data["q"]:
            qs = qs.filter(description__icontains=data["q"])
        if data["category"]:
            qs = qs.filter(category=data["category"])
        if data["date_from"]:
            qs = qs.filter(date__gte=data["date_from"])
        if data["date_to"]:
            qs = qs.filter(date__lte=data["date_to"])
    page = Paginator(qs, 10).get_page(request.GET.get("page"))
    query_params = request.GET.copy()
    query_params.pop("page", None)
    return render(
        request,
        "expenses/expense_list.html",
        {"page": page, "form": form, "query_string": query_params.urlencode()},
    )


@login_required
def expense_create(request):
    form = ExpenseForm(request.POST or None, initial={"date": date.today()})
    if request.method == "POST" and form.is_valid():
        expense = form.save(commit=False)
        expense.user = request.user
        expense.save()
        messages.success(request, "Expense added.")
        return redirect("expense_list")
    return render(request, "expenses/expense_form.html", {"form": form, "title": "Add expense"})


@login_required
def expense_detail(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    return render(request, "expenses/expense_detail.html", {"expense": expense})


@login_required
def expense_update(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    form = ExpenseForm(request.POST or None, instance=expense)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Expense updated.")
        return redirect("expense_list")
    return render(request, "expenses/expense_form.html", {"form": form, "title": "Edit expense"})


@login_required
@require_POST
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    expense.delete()
    messages.success(request, "Expense deleted.")
    return redirect("expense_list")


@login_required
def budget_manage(request):
    today = date.today()
    existing = Budget.objects.filter(user=request.user, month=today.month, year=today.year).first()
    initial = {"month": today.month, "year": today.year}
    form = BudgetForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        # update_or_create keeps one budget per month (matches the DB unique constraint)
        Budget.objects.update_or_create(
            user=request.user,
            month=form.cleaned_data["month"],
            year=form.cleaned_data["year"],
            defaults={"amount": form.cleaned_data["amount"]},
        )
        messages.success(request, "Budget saved.")
        return redirect("budget_manage")
    budgets = Budget.objects.filter(user=request.user)
    return render(request, "expenses/budget.html", {"form": form, "budgets": budgets, "current": existing})
