# FOCUS

Provides APIs to manage pictures. Allows you to group pictures into albums

## Deployment Steps (DEVELOPMENT)

Requirements
Redis Server
Python3

Configuring Celery
These two config variables in (focus.settings.py) stores the host name of the redis server.
CELERY_RESULT_BACKEND
BROKER_URL

```bash

 $ python3 -m venv venv # create virtual environment
 $ . venv/bin/activate
 $(venv) pip install -r requirements.txt
 $(venv) mkdir uploads # for file uploads
 $(venv) cd focus
 $(venv) python3 manage.py migrate
 $(venv) celery -A focus worker --pool=solo -l info
 $(venv) python3 focus/manage.py runserver

```

## API Documentation
