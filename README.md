# FOCUS

Provides APIs to manage pictures. Allows you to group pictures into albums
https://focus-photo-management.herokuapp.com

## Deployment Steps (DEVELOPMENT)

Requirements
Redis Server
Python3

Configuring Celery
These two config variables in (focus.settings.py) stores the host name of the redis server.
`CELERY_RESULT_BACKEND`
`BROKER_URL`

Before running the application , you can set DATABASE URL as an environment variable. This can be done by
`$ export DATABASE_URL=mysql://username:password@localhost:3306/databasename `
You can also set these values directly in the settings.py

```bash

 $ python3 -m venv venv # create virtual environment
 $ . venv/bin/activate
 $(venv) pip install -r requirements.txt
 $(venv) mkdir uploads # for file uploads
 $(venv) cd focus
 $(venv) python3 manage.py migrate
 $(venv) celery -A focus worker --pool=solo -l info
 $(venv) python3 manage.py runserver

```

## Testing

```bash

$(venv) cd focus
$(venv) python3 manage.py test focusapi.tests   # test focus APIs
$(venv) python3 manage.py test user_auth.tests  # test authentication APIs


```

## API Documentation

https://documenter.getpostman.com/view/13293299/UVXkmZyr
