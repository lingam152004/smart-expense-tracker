from django.contrib.auth import views as auth_views
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import api_views, views

router = DefaultRouter()
router.register("expenses", api_views.ExpenseViewSet, basename="api-expense")
router.register("budgets", api_views.BudgetViewSet, basename="api-budget")

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("register/", views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("expenses/", views.expense_list, name="expense_list"),
    path("expenses/add/", views.expense_create, name="expense_create"),
    path("expenses/<int:pk>/", views.expense_detail, name="expense_detail"),
    path("expenses/<int:pk>/edit/", views.expense_update, name="expense_update"),
    path("expenses/<int:pk>/delete/", views.expense_delete, name="expense_delete"),
    path("budget/", views.budget_manage, name="budget_manage"),
    # REST API
    path("api/dashboard/summary/", api_views.dashboard_summary, name="api-summary"),
    path("api/spending/monthly/", api_views.monthly_spending, name="api-monthly"),
    path("api/spending/categories/", api_views.category_spending, name="api-categories"),
    path("api/prediction/", api_views.prediction, name="api-prediction"),
    path("api/insights/", api_views.insights, name="api-insights"),
    path("api/", include(router.urls)),
]
