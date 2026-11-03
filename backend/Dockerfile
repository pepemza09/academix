FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Contenedor sin root: uid 1000 coincide con el dueño del bind-mount
# ./backend:/app en el host, así que media/ y staticfiles/ quedan editables.
RUN useradd --uid 1000 --no-create-home app
RUN mkdir -p /app/media /app/staticfiles && chown -R 1000:1000 /app/media /app/staticfiles
USER 1000:1000

EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--access-logfile", "-"]
