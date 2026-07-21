FROM python:3.11.9-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install --no-install-recommends -y gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py collectstatic --noinput && python manage.py cargar_disc && python manage.py cargar_moss && python manage.py cargar_raven && python manage.py cargar_zavic && python manage.py cargar_competencias && python manage.py cargar_comercial && gunicorn nom035.wsgi --bind 0.0.0.0:8000 --log-file - --timeout 120 --workers 1 --threads 2 --preload"]
