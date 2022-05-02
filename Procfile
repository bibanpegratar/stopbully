cd base
web: gunicorn base.wsgi
release: python backend/base/manage.py makemigrations --noinput
release: python backend/base/manage.py collectstatic --noinput
release: python backend/base/manage.py migrate --noinput