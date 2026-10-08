from datetime import date

from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import services
from .models import Budget, Expense
from .serializers import BudgetSerializer, ExpenseSerializer


class ExpenseViewSet(viewsets.ModelViewSet):
    """CRUD for the logged-in user's expenses only."""

    serializer_class = ExpenseSerializer

    def get_queryset(self):
        # Other users' expenses are never in this queryset, so they return 404.
        return Expense.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@api_view(["GET"])
def dashboard_summary(request):
    return Response(services.dashboard_summary(request.user))


@api_view(["GET"])
def monthly_spending(request):
    data = [
        {"label": date(y, m, 1).strftime("%b %Y"), "year": y, "month": m, "total": total}
        for y, m, total in services.monthly_totals(request.user)
    ]
    return Response(data)


@api_view(["GET"])
def category_spending(request):
    today = date.today()
    scope = request.query_params.get("scope", "month")
    if scope == "all":
        return Response(services.category_totals(request.user))
    return Response(services.category_totals(request.user, today.year, today.month))


@api_view(["GET"])
def prediction(request):
    return Response(services.get_prediction(request.user).to_dict())


@api_view(["GET"])
def insights(request):
    return Response(services.build_insights(request.user))
