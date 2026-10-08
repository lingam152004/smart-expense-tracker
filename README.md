# Smart Expense Tracker with Spending Prediction

A full-stack Django web application for tracking personal expenses, managing monthly budgets, viewing spending charts, and estimating next month's spending with a simple Linear Regression model.

## Features

- Register, log in and log out using Django's built-in authentication
- Add, edit, view and delete expenses (9 categories, 6 payment methods)
- Search and filter expenses by text, category and date range, with pagination
- Monthly budget with alerts at 75%, 90% and 100% (configurable in `settings.py`)
- Dashboard cards: spent this month, budget, remaining, average per day, predicted next month
- Chart.js charts: category doughnut, monthly bar chart, spending trend line
- Rule-based insights (highest/lowest category, month-over-month change, budget usage)
- Next-month spending prediction with scikit-learn Linear Regression
- REST API built with Django REST Framework
- Django admin for users, expenses and budgets
- Automated tests and a `seed_data` command for demo data

## Screenshots

_Add your screenshots here after running the project._

| Dashboard | Expense list | Budget |
|-----------|--------------|--------|
| `docs/screenshots/dashboard.png` | `docs/screenshots/expenses.png` | `docs/screenshots/budget.png` |

## Technology stack

| Layer | Tools |
|-------|-------|
| Backend | Python 3, Django 5, Django REST Framework |
| Database | MySQL (SQLite optional for quick local tests) |
| Frontend | HTML5, CSS3, Bootstrap 5, JavaScript, Chart.js |
| Data / ML | Pandas, NumPy, scikit-learn |

## Architecture

```
Browser (Bootstrap + Chart.js)
        |
   Django URLs  ->  views.py / api_views.py
                          |
                     services.py  (budget, insights, dashboard logic)
                          |
        models.py (MySQL)      ml/spending_predictor.py (pandas + scikit-learn)
```

- `views.py` handles HTML pages and forms.
- `api_views.py` and `serializers.py` expose the REST API.
- `services.py` holds business logic so views stay small.
- `ml/spending_predictor.py` is independent of Django and only works with plain data.

## Database design

**Expense**: `id`, `user` (FK to User), `amount`, `category`, `date`, `payment_method`, `description`, `created_at`. Indexed on (`user`, `date`) and (`user`, `category`).

**Budget**: `id`, `user` (FK to User), `month`, `year`, `amount`, `created_at`. A unique constraint on (`user`, `month`, `year`) allows only one budget per user per month.

Both tables use `on_delete=CASCADE`, so deleting a user removes their data.

## ML approach

1. Sum each user's expenses by month.
2. Clean the data: drop invalid values, merge duplicate months, sort by time, and fill skipped months with 0.
3. Use the month number (1, 2, 3, ...) as the single feature and the monthly total as the target.
4. Train `LinearRegression` and predict the next month.
5. With 6 or more months of data, the last month is held out and the mean absolute error (MAE) is reported. With fewer months no evaluation is shown.

Limitations: it fits a straight line, so it cannot capture seasonality, festivals or one-off purchases. With only a few months of data, treat the number as a rough estimate. At least 3 months of history are required.

## Installation

Requirements: Python 3.10+, MySQL 8, Git.

```bash
git clone <your-repo-url>
cd smart_expense_tracker
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
```

Create the MySQL database:

```sql
CREATE DATABASE expense_tracker CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Copy `.env.example` to `.env` and fill in your values, then:

```bash
python manage.py makemigrations expenses
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_data
python manage.py runserver
```

Open http://127.0.0.1:8000/. Demo login after `seed_data`: `demo_user` / `Demo@12345`.

> If `mysqlclient` fails to install on Windows, see the Troubleshooting section in `docs/SETUP_NOTES.md`, or set `USE_SQLITE=True` in `.env` to try the app without MySQL.

## Environment variables

| Variable | Purpose |
|----------|---------|
| `DJANGO_SECRET_KEY` | Django secret key |
| `DJANGO_DEBUG` | `True` for development, `False` for production |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated host names |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | MySQL connection |
| `USE_SQLITE` | `True` to use SQLite instead of MySQL |

## API endpoints

All endpoints require login (session or HTTP Basic auth) and only return the logged-in user's data.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET, POST | `/api/expenses/` | List / create expenses |
| GET, PUT, PATCH, DELETE | `/api/expenses/<id>/` | Retrieve / update / delete |
| GET, POST | `/api/budgets/` | List / create budgets |
| GET | `/api/dashboard/summary/` | Dashboard summary |
| GET | `/api/spending/monthly/` | Monthly totals |
| GET | `/api/spending/categories/` | Category totals (`?scope=all` for all time) |
| GET | `/api/prediction/` | Next-month prediction |
| GET | `/api/insights/` | Rule-based insights |

## Testing

```bash
python manage.py test
```

Tests cover authentication, expense create/update/delete, budgets, user isolation, and prediction.

## Future improvements

- CSV export and import
- Recurring expenses
- Compare Linear Regression with other models once more data is available
- Docker setup and CI with GitHub Actions
- Token-based API authentication

## Author

**Your Name**
B.Tech in Artificial Intelligence and Data Science | Python Full Stack Developer
GitHub: `<your-github-link>` | LinkedIn: `<your-linkedin-link>`
