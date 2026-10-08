"""Business logic for dashboards, budgets, insights and predictions.

Every function takes a `user` and only queries that user's expenses, so data
from other users can never leak into results.
"""
from collections import defaultdict
from datetime import date
from decimal import Decimal

from django.conf import settings
from django.db.models import Sum
from django.db.models.functions import ExtractMonth, ExtractYear

from .ml.spending_predictor import predict_next_month
from .models import Budget, Expense


def _f(value):
    """Decimal/None -> float for JSON and math."""
    return float(value or 0)


def month_total(user, year, month):
    total = Expense.objects.filter(user=user, date__year=year, date__month=month).aggregate(t=Sum("amount"))["t"]
    return _f(total)


def monthly_totals(user):
    """Return [(year, month, total), ...] sorted oldest to newest."""
    rows = (
        Expense.objects.filter(user=user)
        .annotate(y=ExtractYear("date"), m=ExtractMonth("date"))
        .values("y", "m")
        .annotate(total=Sum("amount"))
        .order_by("y", "m")
    )
    return [(r["y"], r["m"], _f(r["total"])) for r in rows]


def category_totals(user, year=None, month=None):
    qs = Expense.objects.filter(user=user)
    if year and month:
        qs = qs.filter(date__year=year, date__month=month)
    rows = qs.values("category").annotate(total=Sum("amount")).order_by("-total")
    return [{"category": r["category"], "total": _f(r["total"])} for r in rows]


def budget_status(user, year, month):
    """Budget vs spending for one month, plus which alert (if any) applies."""
    budget = Budget.objects.filter(user=user, year=year, month=month).first()
    spent = month_total(user, year, month)
    if not budget:
        return {"has_budget": False, "budget": 0.0, "spent": spent, "remaining": 0.0, "percent_used": 0.0, "alert": None}

    amount = _f(budget.amount)
    percent = round(spent / amount * 100, 1) if amount else 0.0
    alert = None
    for threshold in sorted(settings.BUDGET_ALERT_THRESHOLDS, reverse=True):
        if percent >= threshold:
            level = "danger" if threshold >= 100 else ("warning" if threshold >= 90 else "info")
            text = (
                f"You have exceeded your monthly budget ({percent}% used)."
                if threshold >= 100
                else f"You have used {percent}% of your monthly budget."
            )
            alert = {"threshold": threshold, "level": level, "message": text}
            break
    return {
        "has_budget": True,
        "budget": amount,
        "spent": spent,
        "remaining": round(amount - spent, 2),
        "percent_used": percent,
        "alert": alert,
    }


def average_daily_spending(user, today=None):
    today = today or date.today()
    return round(month_total(user, today.year, today.month) / today.day, 2)


def get_prediction(user):
    return predict_next_month(monthly_totals(user))


def _previous_month(year, month):
    return (year - 1, 12) if month == 1 else (year, month - 1)


def build_insights(user, today=None):
    """Rule-based insights (no AI API). Returns a dict of stats and a list of messages."""
    today = today or date.today()
    y, m = today.year, today.month
    py, pm = _previous_month(y, m)

    this_cats = {c["category"]: c["total"] for c in category_totals(user, y, m)}
    prev_cats = {c["category"]: c["total"] for c in category_totals(user, py, pm)}

    messages = []
    highest = lowest = None
    if this_cats:
        highest = max(this_cats.items(), key=lambda kv: kv[1])
        lowest = min(this_cats.items(), key=lambda kv: kv[1])

    # Rule 1: category increased vs previous month (needs meaningful previous spend)
    for cat, amount in sorted(this_cats.items(), key=lambda kv: -kv[1]):
        prev = prev_cats.get(cat, 0)
        if prev > 0 and amount > prev * 1.2:
            change = round((amount - prev) / prev * 100)
            messages.append(f"{cat} expenses increased by {change}% compared with last month.")

    # Rule 2: Food above the average of all earlier months
    history = defaultdict(list)
    for row in (
        Expense.objects.filter(user=user, category=Expense.Category.FOOD)
        .exclude(date__year=y, date__month=m)
        .annotate(yy=ExtractYear("date"), mm=ExtractMonth("date"))
        .values("yy", "mm")
        .annotate(total=Sum("amount"))
    ):
        history["food"].append(_f(row["total"]))
    if history["food"]:
        avg_food = sum(history["food"]) / len(history["food"])
        if this_cats.get("Food", 0) > avg_food * 1.2:
            messages.append("Your food expenses are higher than your recent average.")

    # Rule 3: budget usage
    status = budget_status(user, y, m)
    if status["alert"]:
        messages.append(status["alert"]["message"])
    elif not status["has_budget"]:
        messages.append("Set a monthly budget to get spending alerts.")

    # Month-over-month change
    this_total, prev_total = month_total(user, y, m), month_total(user, py, pm)
    mom = round((this_total - prev_total) / prev_total * 100, 1) if prev_total > 0 else None

    totals = monthly_totals(user)
    avg_monthly = round(sum(t[2] for t in totals) / len(totals), 2) if totals else 0.0

    if not messages:
        messages.append("Your spending looks steady. Keep logging expenses to unlock more insights.")

    return {
        "highest_category": {"name": highest[0], "total": highest[1]} if highest else None,
        "lowest_category": {"name": lowest[0], "total": lowest[1]} if lowest else None,
        "month_over_month_change": mom,
        "average_monthly_spending": avg_monthly,
        "average_daily_spending": average_daily_spending(user, today),
        "budget_utilization": status["percent_used"],
        "messages": messages,
    }


def dashboard_summary(user, today=None):
    today = today or date.today()
    status = budget_status(user, today.year, today.month)
    prediction = get_prediction(user)
    return {
        "month_label": today.strftime("%B %Y"),
        "total_this_month": status["spent"],
        "budget": status["budget"],
        "has_budget": status["has_budget"],
        "remaining": status["remaining"],
        "percent_used": status["percent_used"],
        "alert": status["alert"],
        "average_daily": average_daily_spending(user, today),
        "prediction": prediction.to_dict(),
    }
