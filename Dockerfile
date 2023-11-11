FROM python:3.11.4-alpine3.17
LABEL maintainer="drosinakis.drosos1@gmail.com"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements-dev.txt /tmp/requirements-dev.txt
COPY ./app /app


WORKDIR /app
EXPOSE 8000


RUN mkdir /coverage  && chmod -R 755 /coverage && \
  python -m venv /py && \
  /py/bin/pip install --upgrade pip && \
  apk add --update --no-cache postgresql-dev gcc python3-dev musl-dev && \
  # apk add --update --no-cache postgresql-client libpq postgresql-libs && \
  # apk add --update --no-cache gcc postgresql-dev musl-dev  && \
  /py/bin/pip install -r /tmp/requirements.txt && \
  /py/bin/pip install -r /tmp/requirements-dev.txt && \
  rm -rf /tmp && \
  adduser \
  --disabled-password \
  --no-create-home \
  django-user && \
  chown -R django-user:django-user /coverage && \
  mkdir -p /vol/web/media && \
  mkdir -p /vol/web/static && \ 
  chown -R django-user:django-user /vol && \
  chmod -R 755 /vol


ENV PATH="/py/bin:$PATH"
USER django-user





