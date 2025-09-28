web: cd TijuanaRoadSafety && gunicorn TijuanaRoadSafety.wsgi:application --bind 0.0.0.0:$PORT
release: cd TijuanaRoadSafety && python manage.py migrate && python manage.py collectstatic --noinput && python manage.py create_admin
