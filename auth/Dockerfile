FROM python:3.10-alpine as base
FROM base as builder
RUN mkdir /install
WORKDIR /install
FROM base
COPY --from=builder /install /usr/local
RUN apk update && apk --no-cache add python3-dev libffi-dev gcc musl-dev make libpq

WORKDIR /auth
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip \
    && pip install -r requirements.txt --default-timeout=1000 --no-cache-dir
COPY . .


WORKDIR /auth/src

ENV PYTHONPATH "${PYTHONPATH}/auth/src"
RUN export PYTHONPATH=.
#CMD ["uvicorn", "wsgi_app:app", "--host", "0.0.0.0", "--port=8001"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "wsgi_app:app"]