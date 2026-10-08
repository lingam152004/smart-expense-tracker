from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from .ml.spending_predictor import INSUFFICIENT_DATA_MESSAGE, predict_next_month
from .models import Budget, Expense


def make_expense(user, amount="100.00", category="Food", when=None, description="test"):
    return Expense.objects.create(
        user=user,
        amount=Decimal(amount),
        category=category,
        date=when or date.today(),
        payment_method="UPI",
        description=description,
    )


class AuthenticationTests(TestCase):
    def test_register_creates_user_with_hashed_password(self):
        response = self.client.post(
            reverse("register"),
            {"username": "newuser", "email": "new@example.com", "password1": "Str0ng!Pass_99", "password2": "Str0ng!Pass_99"},
        )
        self.assertRedirects(response, reverse("dashboard"))
        user = User.objects.get(username="newuser")
        self.assertNotEqual(user.password, "Str0ng!Pass_99")
        self.assertTrue(user.check_password("Str0ng!Pass_99"))

    def test_weak_password_rejected(self):
        response = self.client.post(
            reverse("register"),
            {"username": "weak", "email": "weak@example.com", "password1": "12345678", "password2": "12345678"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="weak").exists())

    def test_login_and_logout(self):
        User.objects.create_user("alice", password="Str0ng!Pass_99")
        self.assertTrue(self.client.login(username="alice", password="Str0ng!Pass_99"))
        self.assertEqual(self.client.get(reverse("dashboard")).status_code, 200)
        self.client.post(reverse("logout"))
        self.assertEqual(self.client.get(reverse("dashboard")).status_code, 302)

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)


class ExpenseCrudTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("alice", password="Str0ng!Pass_99")
        self.client.login(username="alice", password="Str0ng!Pass_99")

    def test_create_expense(self):
        response = self.client.post(
            reverse("expense_create"),
            {"amount": "250.50", "category": "Food", "date": date.today().isoformat(), "payment_method": "UPI", "description": "Lunch"},
        )
        self.assertRedirects(response, reverse("expense_list"))
        expense = Expense.objects.get()
        self.assertEqual(expense.user, self.user)
        self.assertEqual(expense.amount, Decimal("250.50"))

    def test_invalid_amount_rejected(self):
        response = self.client.post(
            reverse("expense_create"),
            {"amount": "-5", "category": "Food", "date": date.today().isoformat(), "payment_method": "UPI"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Expense.objects.count(), 0)

    def test_future_date_rejected(self):
        response = self.client.post(
            reverse("expense_create"),
            {"amount": "10", "category": "Food", "date": "2999-01-01", "payment_method": "UPI"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Expense.objects.count(), 0)

    def test_update_expense(self):
        expense = make_expense(self.user)
        self.client.post(
            reverse("expense_update", args=[expense.pk]),
            {"amount": "999.00", "category": "Bills", "date": date.today().isoformat(), "payment_method": "Cash", "description": "Updated"},
        )
        expense.refresh_from_db()
        self.assertEqual(expense.amount, Decimal("999.00"))
        self.assertEqual(expense.category, "Bills")

    def test_delete_expense(self):
        expense = make_expense(self.user)
        self.client.post(reverse("expense_delete", args=[expense.pk]))
        self.assertFalse(Expense.objects.filter(pk=expense.pk).exists())

    def test_delete_requires_post(self):
        expense = make_expense(self.user)
        response = self.client.get(reverse("expense_delete", args=[expense.pk]))
        self.assertEqual(response.status_code, 405)
        self.assertTrue(Expense.objects.filter(pk=expense.pk).exists())

    def test_filter_by_category(self):
        make_expense(self.user, category="Food")
        make_expense(self.user, category="Travel")
        response = self.client.get(reverse("expense_list"), {"category": "Travel"})
        self.assertEqual(len(response.context["page"].object_list), 1)


class BudgetTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("alice", password="Str0ng!Pass_99")
        self.client.login(username="alice", password="Str0ng!Pass_99")

    def test_create_budget(self):
        today = date.today()
        response = self.client.post(reverse("budget_manage"), {"month": today.month, "year": today.year, "amount": "25000"})
        self.assertRedirects(response, reverse("budget_manage"))
        self.assertEqual(Budget.objects.get().amount, Decimal("25000.00"))

    def test_saving_same_month_updates_instead_of_duplicating(self):
        today = date.today()
        for amount in ("20000", "30000"):
            self.client.post(reverse("budget_manage"), {"month": today.month, "year": today.year, "amount": amount})
        self.assertEqual(Budget.objects.count(), 1)
        self.assertEqual(Budget.objects.get().amount, Decimal("30000.00"))

    def test_database_blocks_duplicate_month(self):
        Budget.objects.create(user=self.user, month=1, year=2026, amount=1000)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Budget.objects.create(user=self.user, month=1, year=2026, amount=2000)

    def test_alert_at_threshold(self):
        today = date.today()
        Budget.objects.create(user=self.user, month=today.month, year=today.year, amount=1000)
        make_expense(self.user, amount="920.00")
        response = self.client.get(reverse("api-summary"))
        self.assertEqual(response.json()["alert"]["threshold"], 90)


class UserIsolationTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user("alice", password="Str0ng!Pass_99")
        self.bob = User.objects.create_user("bob", password="Str0ng!Pass_99")
        self.bob_expense = make_expense(self.bob, amount="500.00", description="bob private")
        self.client.login(username="alice", password="Str0ng!Pass_99")

    def test_cannot_view_other_users_expense(self):
        self.assertEqual(self.client.get(reverse("expense_detail", args=[self.bob_expense.pk])).status_code, 404)

    def test_cannot_edit_or_delete_other_users_expense(self):
        self.assertEqual(self.client.get(reverse("expense_update", args=[self.bob_expense.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse("expense_delete", args=[self.bob_expense.pk])).status_code, 404)
        self.assertTrue(Expense.objects.filter(pk=self.bob_expense.pk).exists())

    def test_list_only_shows_own_expenses(self):
        make_expense(self.alice, description="alice own")
        response = self.client.get(reverse("expense_list"))
        self.assertEqual([e.user for e in response.context["page"].object_list], [self.alice])

    def test_api_only_returns_own_expenses(self):
        make_expense(self.alice)
        data = self.client.get("/api/expenses/").json()
        self.assertEqual(len(data), 1)
        self.assertEqual(self.client.get(f"/api/expenses/{self.bob_expense.pk}/").status_code, 404)

    def test_api_requires_authentication(self):
        self.client.logout()
        self.assertIn(self.client.get("/api/expenses/").status_code, (401, 403))


class PredictionTests(TestCase):
    def test_insufficient_data_message(self):
        result = predict_next_month([(2026, 1, 1000), (2026, 2, 1200)])
        self.assertFalse(result.success)
        self.assertEqual(result.message, INSUFFICIENT_DATA_MESSAGE)

    def test_linear_trend_prediction(self):
        data = [(2026, 1, 15000), (2026, 2, 16500), (2026, 3, 17000), (2026, 4, 18000), (2026, 5, 19500), (2026, 6, 20000)]
        result = predict_next_month(data)
        self.assertTrue(result.success)
        self.assertEqual(result.next_month_label, "July 2026")
        self.assertAlmostEqual(result.predicted_amount, 21166.67, places=2)
        self.assertIsNotNone(result.mae)

    def test_prediction_never_negative(self):
        result = predict_next_month([(2026, 1, 3000), (2026, 2, 1000), (2026, 3, 100)])
        self.assertGreaterEqual(result.predicted_amount, 0)

    def test_api_prediction_endpoint(self):
        user = User.objects.create_user("alice", password="Str0ng!Pass_99")
        self.client.login(username="alice", password="Str0ng!Pass_99")
        response = self.client.get(reverse("api-prediction"))
        self.assertFalse(response.json()["success"])
