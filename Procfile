release: python3 focus/manage.py migrate
web: gunicorn --pythonpath focus focus.wsgi --log-file -