FROM python:3.10-alpine as base
FROM base as builder
WORKDIR /install
FROM base
COPY --from=builder /install /usr/local
RUN apk update && apk --no-cache add python3-dev libffi-dev gcc musl-dev make libpq g++

WORKDIR /auth
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip \
    && pip install -r requirements.txt --default-timeout=1000 --no-cache-dir
COPY . .


WORKDIR /auth/src

ENV PYTHONPATH "${PYTHONPATH}/auth/src"
RUN export PYTHONPATH=.
RUN chmod u+x ./script/run_auth.sh
ENTRYPOINT ["./script/run_auth.sh"]