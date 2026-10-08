# Interview preparation

Answer in your own words. Only claim what you actually built and can run.

## Python
**Why Python?** It is readable, has a huge ecosystem for both web (Django) and data science (Pandas, scikit-learn), so one language covered the whole project.

**Which concepts did you use?** Functions, classes and dataclasses, list comprehensions, modules and packages, virtual environments, environment variables, and exception handling.

## Django
**Why Django?** It comes with authentication, an ORM, an admin panel, form validation and CSRF protection built in, which lets me focus on the application logic.

**What is MVT?** Model-View-Template. The *model* defines data (`models.py`), the *view* handles a request and returns a response (`views.py`), the *template* is the HTML. URLs map an address to a view.

**How does authentication work?** Django stores users in its `User` model with hashed passwords. On login it creates a session and sends a session cookie. `@login_required` redirects anonymous visitors to the login page.

## MySQL
**Explain your database design.** Two main tables, `Expense` and `Budget`, each linked to Django's `User` by a foreign key. Budget has a unique constraint on (user, month, year). Expense has indexes on (user, date) and (user, category) because most queries filter by user and date.

**What relationships did you use?** One-to-many: one user has many expenses and many budgets.

**Important queries?** Filtering a user's expenses, summing amounts grouped by month, and summing grouped by category. The ORM's `filter`, `values`, `annotate` and `Sum` do this.

## Machine Learning
**Why Linear Regression?** It is simple, fast, easy to explain, and suitable when there are only a few monthly data points. A complex model would overfit.

**What is training data?** The past monthly totals the model learns from.

**What is a feature?** An input variable. Mine is the month number (1, 2, 3, ...). The target is the monthly total.

**How does prediction work?** The model fits a straight line through past totals and extends it one month ahead.

**How did you evaluate it?** With 6 or more months, I hold out the latest month, train on the rest, and report mean absolute error. With fewer months it is not evaluated, and the app says so.

**Limitations?** It only sees the trend. It ignores seasonality, festivals, salary changes and one-off purchases, and with few months of data the estimate is rough.

## Project
**Architecture?** Django serves HTML pages and a REST API. Views call a services layer, which uses the ORM and a separate ML module. Chart.js reads JSON from the API.

**How is user data protected?** Every query filters by `request.user`, other users' records return 404, API endpoints require authentication, passwords are hashed, CSRF protection is on, and secrets live in environment variables.

**Hardest part?** Prepare your own honest answer. Good candidates: cleaning monthly data with skipped months, or keeping user data isolated in both the web pages and the API.

**What would you improve?** CSV import/export, recurring expenses, token authentication, Docker and CI, and comparing other models when more data exists.
