# Setup notes and common errors

## Windows installation checklist
1. Python 3.10 or newer from python.org (tick "Add Python to PATH").
2. MySQL Community Server 8 and MySQL Workbench from mysql.com.
3. Git from git-scm.com.
4. VS Code (optional).

## Common errors

| Error | Fix |
|-------|-----|
| `pip install mysqlclient` fails on Windows | Upgrade pip (`python -m pip install --upgrade pip`) and retry; recent versions ship prebuilt wheels. If it still fails, use `USE_SQLITE=True` in `.env` to continue without MySQL. |
| `Access denied for user 'root'` | Check `DB_USER` and `DB_PASSWORD` in `.env`. |
| `Unknown database 'expense_tracker'` | Run the `CREATE DATABASE` statement from the README. |
| `no such table: expenses_expense` or tests fail with missing tables | Run `python manage.py makemigrations expenses` and then `python manage.py migrate`. |
| `ModuleNotFoundError: No module named 'django'` | Activate the virtual environment: `venv\Scripts\activate`. |
| Charts stay empty | Run `python manage.py seed_data`, hard-refresh the page, and check the browser console. The charts load Chart.js from a CDN, so internet access is needed. |
