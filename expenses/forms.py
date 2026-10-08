from datetime import date

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Budget, Expense


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ["amount", "category", "date", "payment_method", "description"]
        widgets = {
            "amount": forms.NumberInput(attrs={"step": "0.01", "min": "0.01", "class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "payment_method": forms.Select(attrs={"class": "form-select"}),
            "description": forms.TextInput(attrs={"class": "form-control", "placeholder": "Optional note"}),
        }

    def clean_date(self):
        value = self.cleaned_data["date"]
        if value > date.today():
            raise forms.ValidationError("Expense date cannot be in the future.")
        return value


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ["month", "year", "amount"]
        widgets = {
            "month": forms.Select(
                choices=[(i, date(2000, i, 1).strftime("%B")) for i in range(1, 13)],
                attrs={"class": "form-select"},
            ),
            "year": forms.NumberInput(attrs={"class": "form-control", "min": 2000, "max": 2100}),
            "amount": forms.NumberInput(attrs={"step": "0.01", "min": "0.01", "class": "form-control"}),
        }


class ExpenseFilterForm(forms.Form):
    q = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Search description"}))
    category = forms.ChoiceField(
        required=False,
        choices=[("", "All categories")] + list(Expense.Category.choices),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}))
