# Deployment guide (PythonAnywhere, beginner-friendly)

PythonAnywhere offers a free tier with MySQL support, which matches this project.

1. Push the project to GitHub (make sure `.env` is not committed).
2. Create a PythonAnywhere account and open a Bash console.
3. Clone your repo, create a virtualenv, and `pip install -r requirements.txt`.
4. On the **Databases** tab, create a MySQL database and note the host, name and user.
5. Create a `.env` file on the server:
   ```
   DJANGO_SECRET_KEY=<a long random value>
   DJANGO_DEBUG=False
   DJANGO_ALLOWED_HOSTS=<yourusername>.pythonanywhere.com
   DB_NAME=<yourusername>$expense_tracker
   DB_USER=<yourusername>
   DB_PASSWORD=<your database password>
   DB_HOST=<yourusername>.mysql.pythonanywhere-services.com
   DB_PORT=3306
   CSRF_TRUSTED_ORIGINS=https://<yourusername>.pythonanywhere.com
   ```
   Generate a secret key with:
   `python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"`
6. Run `python manage.py makemigrations expenses` (if migrations are not committed), `python manage.py migrate`, `python manage.py collectstatic`, and `python manage.py createsuperuser`.
7. On the **Web** tab, add a web app (manual configuration), set the virtualenv path, and edit the WSGI file so it points to `config.settings`.
8. Map the `/static/` URL to your `staticfiles` directory.
9. Reload the web app.

## Production notes
- `DJANGO_DEBUG=False` enables secure cookies and HTTPS redirect (see `settings.py`).
- WhiteNoise serves static files when running behind Gunicorn on platforms such as Render or Railway. The start command would be `gunicorn config.wsgi`.
- Never put real secrets in the repository.
