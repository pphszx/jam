FROM python:3.6.9

ENV FLASK_ENV=production \
    FLASK_APP="jam.__init__:create_app()" \
    JAM_CONFIG=production \
    JAM_PORT=5000 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN useradd --user-group --no-create-home --no-log-init --shell /bin/bash jam \
    && python -m pip install -r requirements.txt

WORKDIR /app
COPY . /app

USER jam

EXPOSE 5000

ENTRYPOINT ["bash", "/app/docker/docker-entrypoint.sh"]
