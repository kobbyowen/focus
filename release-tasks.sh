python3 focus/manage.py migrate 
mkdir uploads
cd focus
celery -A focus worker --pool=solo -l info