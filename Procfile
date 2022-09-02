web: python manage.py collectstatic --no-input
web: gunicorn YOLO.asgi -k uvicorn.workers.UvicornWorker